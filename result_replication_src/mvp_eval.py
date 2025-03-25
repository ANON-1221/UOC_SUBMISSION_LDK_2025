import json
import re
import pandas as pd
import numpy as np
# from utils.post_process import ProcessPred
import os
import csv
import sys
sys.path.append('../') 
from evaluations.opinion_overlap_eval import OpinionEval


class ProcMvpRes:
    """
    Impl so far:
    
        1. tup_em ACOS results gen_scl_nat
        2. comp_lev uoce results for gen_scl_nat
    
    remaining:
        1. comp_em ACOS results
    """
    def __init__(self, pred_res_path, gold_annot_path):
        self.pred_res_path = pred_res_path
        self.gold_annot_path = gold_annot_path
        self.category_subs = {'general': 'overall', 
                 'style_options': "styles and options",
                 'design_features': 'features',
                 'operation_performance': 'performance'}

        with open(pred_res_path, 'r') as f:
            self.acos_mvp = json.load(f)

    def entity_category_mvp(self, stx):
        entcat = stx.split(' ')
        if len(entcat) != 2:
            category = 'general'
            entity = entcat[0]
        else:
            entity = entcat[0]
            category = entcat[1]
        return [entity, category]            

    def calc_tup_em_acos(self, mode='acos'):
        TP = 0
        FP = 0
        N_PRED = 0
        N_GOLD = 0

        mode_index = {
            'aste':[2, 3, 4],
            'acos': [0, 1, 2, 3, 4]
        }
        
        INCL_PROPERTY = mode_index[mode]

        for rec in self.acos_mvp:
            pred_labs = []
            gold_labs = []
            for gelems in rec['gold']:
                gentcat, gasp, gpol, gop = gelems
                gold_labs.append([*gentcat.split(' '), gasp, gpol, gop])
            for pelems in rec['pred']:
                pentcat, pasp, ppol, pop = pelems
                pred_labs.append([*pentcat.split(' '), pasp, ppol, pop])
            # INCL_PROPERTY = [0, 1, 2, 3, 4]
            gold = set(['-'.join([x for i, x in enumerate(rx) if i in INCL_PROPERTY]) for rx in gold_labs])
            pred = set(['-'.join([x for i, x in enumerate(rx) if i in INCL_PROPERTY]) for rx in pred_labs])          
            intersect = gold.intersection(pred)
            TP+=len(intersect)
            # if len(intersect)>0:
            #     print(intersect)
            N_PRED += len(pred)
            N_GOLD += len(gold)

        precision = TP/(N_PRED)
        recall = TP/(N_GOLD)
        f1_score = 2*precision*recall/(precision+recall)
        # print(f'Hits: {TP}, precision: {precision*100}, recall: {recall*100} , f1_score: {f1_score*100}')
        return precision, recall, f1_score
    
    def calc_comp_em_acos(self, mode='acos'):
        colname_dict = {
            'acos':['target_entity', 'aspect_category','aspect_term', 'sentiment_polarity', 'sentiment_expression'],
            'aste': ['aspect_term', 'sentiment_polarity', 'sentiment_expression']
        }
        colname = colname_dict[mode]
        result_list = []

        for rec in self.acos_mvp:
            if mode=='acos':
                pred1 = [{colname[i]:v for i, v in enumerate(self.entity_category_mvp(val[0])+val[1:])} for val in rec['pred']]
                gold1 = [{colname[i]:v for i, v in enumerate(self.entity_category_mvp(val[0])+val[1:])} for val in rec['gold']]
            else:
                pred1 = [{colname[i]:v for i, v in enumerate(val[1:])} for val in rec['pred']]
                gold1 = [{colname[i]:v for i, v in enumerate(val[1:])} for val in rec['gold']]
            result_list.append({
                'gold': gold1,
                'pred': pred1
            })
        TP = 0
        TOT_PRED = 0
        TOT_GOLD = 0
        opeval = OpinionEval(colname)
        for i in range(len(result_list)):
            gold_arx = result_list[i]['gold']
            pred_arx = result_list[i]['pred']
            tp, _, _ = opeval.one_input_pred_metrics(gold_arx, pred_arx)
            TP += tp
            TOT_PRED += len(pred_arx)
            TOT_GOLD += len(gold_arx)

        precision = TP/TOT_PRED
        recall = TP/TOT_GOLD
        f1_score = 2 * precision * recall / (precision + recall)
        
        # print(f'precision: {precision}, recall: {recall}, f1-score: {f1_score}')
        return precision, recall, f1_score
    
    def calc_comp_em_uoce(self):
        """
        Calculations using the tailored metrics introduced by us

        """
        pol_dict = {
            'POS': 'positive',
            'NEG': 'negative',
            'NEU': 'neutral'
        }
        # loading and processing gold annotations
        df_gold = pd.read_csv(self.gold_annot_path)
        df_gold = df_gold.fillna('NULL')

        res_acc = []
        curr_id = None
        curr_acc = {'gold_labs': []}
        for row in df_gold.values:
            idx, sent, *opinion = row
            aterm, ospan, entx, catx, pol, hldr, hldr_e, sent_ent, qual, reason = opinion
            elem_dict = {'aspect_term': aterm, 
                        'sentiment_expression': ospan,
                        'target_entity': entx, 
                        'aspect_category': catx, 
                        'sentiment_polarity':pol_dict[pol],
                        'opinion_holder_span': hldr, 
                        'opinion_holder_entity': hldr_e, 
                        'sentiment_intensity': sent_ent,
                        'opinion_qualifier': qual, 
                        'opinion_reason': reason 
                        }

            if idx!='NULL':
                if curr_id:
                    res_acc.append(curr_acc)
                    curr_acc = {'gold_labs': []}
                curr_id=idx
                curr_acc['sent'] = sent.lower().replace(" ", '').strip()
                curr_acc['id'] = idx
                curr_acc['gold_labs'].append(elem_dict)
            else:
                curr_acc['gold_labs'].append(elem_dict)

        if 'id' in curr_acc.keys():
            res_acc.append(curr_acc)


        mvp_res_all = []

        for rec in self.acos_mvp:
            pred_labs = []
            rec_dict = {
                'sent': "".join(rec['sent']).lower().replace(" ", '').strip()
            }
            for pelems in rec['pred']:
                pentcat, pasp, ppol, pop = pelems
                
                splitentcat = pentcat.split(' ')
                if len(splitentcat)==2:
                    entfin, catefin = splitentcat
                else:
                    entfin = 'NULL'
                    catefin = splitentcat[0]
                pred_labs.append({'aspect_term': pasp, 
                        'sentiment_expression': pop,
                        'target_entity': entfin.lower(), 
                        'aspect_category': catefin.lower(), 
                        'sentiment_polarity':ppol,
                        'opinion_holder_span': 'NULL', 
                        'opinion_holder_entity': 'NULL', 
                        'sentiment_intensity': 'NULL',
                        'opinion_qualifier': 'NULL', 
                        'opinion_reason': 'NULL' 
                            })
                
            rec_dict['pred'] = pred_labs
            mvp_res_all.append(rec_dict)

        combined_mvp = []
        for rec in res_acc:
            ref_sent = rec['sent']
            no_match = True
            for mvp_rec in mvp_res_all:
                qsent = mvp_rec['sent']
                if qsent==ref_sent:
                    no_match = False
                    combined_mvp.append({
                        'sent': ref_sent,
                        'id': rec['id'],
                        'preds': mvp_rec['pred'],
                        'golds': rec['gold_labs']
                    })
            if no_match:
                raise ValueError('NO')
        
        colname = ['target_entity', 'aspect_category','aspect_term', 'sentiment_polarity', 
           'sentiment_expression', 'opinion_holder_span','opinion_holder_entity', 
           'sentiment_intensity', 'opinion_qualifier', 'opinion_reason']
        
        opeval = OpinionEval(colname)
        TP = 0
        TPREDS = 0
        TGOLDS = 0
        for rec in combined_mvp:
            preds = rec['preds']
            golds = rec['golds']
            tp, _, _ = opeval.one_input_pred_metrics(golds, preds)
            TP += tp
            TPREDS += len(preds)
            TGOLDS += len(golds)

        p = TP/TPREDS
        r = TP/TGOLDS
        f1 = 2*p*r/(p+r)
        # print(f'UOCE (MVP) ---> Precision: {p}, recall: {r}, F1: {f1}')
        return p, r, f1