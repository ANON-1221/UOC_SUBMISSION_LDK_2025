import pandas as pd
import numpy as np
import argparse
import os

class OpinionEval:
    def __init__(self, col_labs) -> None:
        self.columns_incls = col_labs

    def check_value_nan(self, val):
        if not isinstance(val, float):
            return False
        else:
            return np.isnan(val)
    
    
    def sel_match_matrix(self, ref, res_mod):
        tot_ref = len(ref)
        total_res = len(res_mod)
        match_matrix = np.zeros(shape=(tot_ref, total_res))
        for ref_i in range(tot_ref):
            for res_j in range(total_res):
                ref_dict = ref[ref_i]
                res_dict = res_mod[res_j]
                match_col = ['aspect_term', 'sentiment_expression']
                res_match = [(ref_dict[col] == res_dict[col]) for col in match_col]
                match_matrix[ref_i, res_j] = sum([res_value for res_value in res_match if res_value is True])
        ax = np.dstack(np.unravel_index(np.argsort(match_matrix, axis=None), match_matrix.shape))
        ax = np.flip(ax, axis=1)

        final_picks = []
        zero_index = []
        last_index = []
        for i, (tx1, tx2) in enumerate(ax[0]):
            if i==0:
                final_picks.append([tx1, tx2])
                zero_index.append(tx1)
                last_index.append(tx2)
            if tx1 not in zero_index and tx2 not in last_index:
                final_picks.append([tx1, tx2])
                zero_index.append(tx1)
                last_index.append(tx2)  
        return final_picks
    
    def get_predicted_rows(self, df, g_idx):
        collected_rows = []
        matched_index = None
        for row in df[self.columns_incls].to_dict(orient='records'):
            idx = row['id']
            if idx is not np.nan:
                if idx == g_idx:
                    matched_index=idx
                    collected_rows.append(row)
                elif matched_index is not None:
                    break
            else:
                if matched_index:
                    collected_rows.append(row)
        return collected_rows
    
    def get_all_gold_rows(self, gold_df, g_id):
        collected_rows = []
        matched_index = None
        for row in gold_df[self.columns_incls].to_dict(orient='records'):
            idx = row['id']
            if idx is not np.nan:
                if g_id==idx:
                    matched_index = idx
                    collected_rows.append(row)
                else:
                    if matched_index:
                        break
            else:
                if matched_index is not None:
                        collected_rows.append(row)
        return collected_rows
    
    def get_correct_incorrect_matches(self, gold_dict, pred_dict):
        tp = []
        fp = []
        fn = []
        for col in self.columns_incls:
            # try:

            if col not in ['id', 'raw_text']:
                # print(f'Extracting: {col}')
                p_val = pred_dict[col]
                g_val = gold_dict[col]
                if  self.check_value_nan(p_val) and  not self.check_value_nan(g_val):
                    fn.append(g_val.lower().strip())
                elif not self.check_value_nan(p_val) and self.check_value_nan(g_val):
                    fp.append(p_val.lower().strip())
                else:
                    if self.check_value_nan(p_val) and self.check_value_nan(g_val):
                        
                        tp.append(p_val)
                    elif p_val.lower().strip() == g_val.lower().strip():
                        tp.append(p_val)
                    elif p_val.lower().strip() != g_val.lower().strip():
                        fp.append(p_val)
                        fn.append(g_val)
            # except Exception as exp:
            #     # print('exception', col, type(g_val), type(p_val), np.isnan(p_val), np.isnan(g_val is float("nan"))
            #     exit(-1)
        return {
            'ntp': len(tp),
            'nfp': len(fp),
            'nfn': len(fn),
            'tot': len(self.columns_incls) #- 1
        }

    def one_input_pred_metrics(self, gold_dicts, pred_dicts):
        tp = 0
        fp = 0
        fn = 0
        ## taking care of matched preds

        used_idx_gold = []
        used_idx_pred = []
        matched_preds = self.sel_match_matrix(gold_dicts, pred_dicts)
        for g_ind, p_ind in matched_preds:
            p_dict = pred_dicts[p_ind]
            g_dict = gold_dicts[g_ind]
            used_idx_gold.append(g_ind)
            used_idx_pred.append(p_ind)
            stats_dict = self.get_correct_incorrect_matches(g_dict, p_dict)
            fp += stats_dict['nfp']/stats_dict['tot']
            tp += stats_dict['ntp']/stats_dict['tot']
            fn += stats_dict['nfn']/stats_dict['tot']

        fp += len(pred_dicts) - len(used_idx_pred)
        fn += len(gold_dicts) - len(used_idx_gold)
        
        return tp, fp, fn
    
    def eval_opinions(self, gold_df, pred_df):
        TP = 0
        FP = 0
        FN = 0
        tot_gold = 0
        tot_pred = 0
        

        for ids in gold_df['id'].values:
            if ids is not np.nan:
                gold_dicts = self.get_all_gold_rows(gold_df, ids)
                pred_dicts = self.get_predicted_rows(pred_df, ids)
                
                tot_gold += len(gold_dicts)
                tot_pred += len(pred_dicts)
                tp, fp, fn = self.one_input_pred_metrics(gold_dicts, pred_dicts)
                TP+=tp
                FP+=fp
                FN+=fn

        precision = TP/tot_pred #(TP+FP)
        recall = TP/tot_gold #(TP+FN)
        f1 = (2*precision*recall)/(precision+recall)
        return {
            'precision':precision,
            'recall':recall,
            'f1': f1
        }


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'data parameters')
    parser.add_argument('--gold_csv', help='training key to use')
    parser.add_argument('--pred_csv', help='gpu device visible')
    args = parser.parse_args()



    RES_PATH = '../ontology_experiments/results/final_results/'

    dict_pol = {
        'POS': 'positive',
        'NEG': 'negative',
        'NEU': 'neutral'
    }

    columns_incls = ['id', 'raw_text', 'aspect_term', 'sentiment_expression', 'target_entity', 'aspect_category', 'sentiment_polarity', 'opinion_holder_span', 'opinion_holder_entity', 'sentiment_intensity', 'opinion_qualifier', 'opinion_reason']
    op_eval = OpinionEval(col_labs=columns_incls)

    GOLD_PATH = os.path.join(RES_PATH, args.gold_csv)
    PRED_PATH = os.path.join(RES_PATH, args.pred_csv)

    gold_df = pd.read_csv(GOLD_PATH).replace({'sentiment_polarity': dict_pol})
    pred_df = pd.read_csv(PRED_PATH)

    print(op_eval.eval_opinions(gold_df, pred_df))