import numpy as np
import json

def create_count_dict(ar):
    ard = {}
    for xi in ar:
        if xi not in ard:
            ard[xi] = 0       
        ard[xi] += 1
    return ard

def overlap_dict(gold_dict, pred_dict):
    tp_arr = {}
    # true positive (given the number of times it occurs in gold_dict>1) if:
    # it n(pred_dict)<=gold_dict then n(pred_dict)
    # if n(pred_dict)>gold_dict then TP=n(gold_dict), FP = pred_dict-gold_dict
    # if n()
    fp_arr = {}
    fn_arr = {}
    for gk in gold_dict:
        gk_num = gold_dict.get(gk, 0)
        pk_num = pred_dict.get(gk, 0)
        # print(gk, gk_num, pk_num)
        if gk_num >= pk_num:
            tp_arr[gk]= pk_num
            fn_arr[gk] = gk_num-pk_num # term is supposed to be extracted but is not extracted
    for pk in pred_dict:
        gk_num = gold_dict.get(pk, 0)
        pk_num = pred_dict.get(pk, 0)
        if pk_num>gk_num:
            fp_arr[pk] = pk_num-gk_num
            tp_arr[pk] = gk_num
    
    return tp_arr, fp_arr, fn_arr
def check_and_insert(targ_dict: dict, gold: list, pred: list) -> dict:
    TP_INDEX = 0
    FP_INDEX = 1
    FN_INDEX = 2
    GOLD_CNT = 3
    PRED_CNT = 4
    gold_dict = create_count_dict(gold)
    pred_dict = create_count_dict(pred)
    TP, FP, FN = overlap_dict(gold_dict, pred_dict)
 
    for k in TP:
        if k not in targ_dict.keys():
            targ_dict[k] = [0, 0, 0, 0, 0]
        targ_dict[k][TP_INDEX]+= TP[k]
    
    for k in FP:
        if k not in targ_dict.keys():
            targ_dict[k] = [0, 0, 0, 0, 0]
        targ_dict[k][FP_INDEX]+= FP[k]

    for k in FN:
        if k not in targ_dict.keys():
            targ_dict[k] = [0, 0, 0, 0, 0]
        targ_dict[k][FN_INDEX]+= FN[k]

    for k in gold_dict:
        if k not in targ_dict.keys():
            targ_dict[k] = [0, 0, 0, 0, 0]
        targ_dict[k][GOLD_CNT] += gold_dict[k]


    for k in pred_dict:
        if k not in targ_dict.keys():
            targ_dict[k] = [0, 0, 0, 0, 0]
        targ_dict[k][PRED_CNT] += 1

    return targ_dict


def calc_labs(pred_gold_lab_list):
    result_count_dict = {}
    accumulated_score = [0, 0, 0]  # PRECISION, RECALL, F1
    for i, (pred, gold) in enumerate(pred_gold_lab_list):
        pred_set = [xi.lower().strip() for xi in pred if xi.strip() and 'none' not in xi]
        gold_set = [xi.lower().strip() for xi in gold if xi.strip() and 'none' not in xi]
        print(pred_set, gold_set)
        result_count_dict = check_and_insert(result_count_dict, gold_set, pred_set)
    TP, FP, FN, T_LABS, T_PRED = np.array(list(result_count_dict.values())).sum(axis=0)
    precision = TP/(TP+FP+0.0001)
    recall = TP/(TP+FN+0.0001)
    denominator = precision+recall
    f1 = (2 * precision * recall)/denominator if denominator>0 else 0

    return (precision, recall, f1)

def calc_labs2(pred_gold_lab_list):
    result_count_dict = {}
    accumulated_score = [0, 0, 0]  # PRECISION, RECALL, F1
    for i, (pred, gold) in enumerate(pred_gold_lab_list):
        pred_set = [xi.lower().strip() for xi in pred if xi.strip() and 'none' not in xi]
        gold_set = [xi.lower().strip() for xi in gold if xi.strip() and 'none' not in xi]
        print(pred_set, gold_set)
        result_count_dict = check_and_insert(result_count_dict, gold_set, pred_set)
    TP, FP, FN, T_LABS, T_PRED = np.array(list(result_count_dict.values())).sum(axis=0)
    precision = TP/T_PRED
    recall = TP/T_LABS
    denominator = precision+recall
    f1 = (2 * precision * recall)/denominator if denominator>0 else 0

    return (precision, recall, f1)
