#  Copyright (c) Meta Platforms, Inc. and affiliates.
#  All rights reserved.
#
#  This source code is licensed under the license found in the
#  LICENSE file in the root directory of this source tree.

import argparse
import jsonlines
import numpy as np
from scipy.stats import kendalltau
from pycocoevalcap.bleu.bleu import Bleu
from pycocoevalcap.cider.cider import Cider
from pycocoevalcap.rouge.rouge import Rouge

# Generated caption for the video clip
# e.g., pred_data = [
#     {"generated_text": "the person is chopping a red onion, instead of a green onion."},
#     {"generated_text": "the person is using a red bell pepper, instead of a red chili pepper."}
#     ...
# ]
def evaluate_diffcap(gt_data, pred_data):

    hypothesis = {str(idx): [pred['generated_text']] for idx, pred in enumerate(pred_data)}
    reference = {str(idx): entry['text'] for idx, entry in enumerate(gt_data)}

    results = {
        'BLEU': Bleu().compute_score(reference, hypothesis)[0][0],
        'CIDEr': Cider().compute_score(reference, hypothesis)[0],
        'ROUGE-L': Rouge().compute_score(reference, hypothesis)[0],
    }
    return results

# Probabilities / matching scores for each candidate pair of videos
# e.g., pred_data = [
#   {"scores": [0.195, 0.088, 0.122, 0.593]},
#   {"scores": [0.275, 0.634, 0.038, 0.051]}
#     ...
# ]
def evaluate_diffmcq(gt_data, pred_data):

    targets = [annot['options'].index(annot['answer']) for annot in gt_data]
    targets = np.array(targets)

    pred_scores = np.array([pred['scores'] for pred in pred_data])
    predictions = pred_scores.argmax(1)

    acc = (predictions==targets).mean()
    results = {
        'accuracy': acc
    }
    return results

# Ranking score for each candidate video compared to the reference
# e.g., pred_data = [
#   {"scores": [0.004, 0.058, 0.936, 0.101]}
#   {"scores": [0.010, 0.002, 0.492, 0.493]}
#     ...
# ]
def evaluate_diffrank(gt_data, pred_data):

    target_scores = [annot['scores'] for annot in gt_data]
    pred_scores = [pred['scores'] for pred in pred_data]

    taus = []
    for preds, targets in zip(pred_scores, target_scores):
        tau = kendalltau(preds, targets).correlation
        taus.append(tau)
    ktau = np.mean(taus)
    results = {
        'ktau': ktau
    }
    return results


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--gt_file', help='path to ground truth dataset jsonl')
    parser.add_argument('--pred_file', help='path to prediction jsonl')
    parser.add_argument('--task', help='diffcap, diffmcq, diffrank')
    args = parser.parse_args()

    if args.task == 'diffcap':
        eval_fn = evaluate_diffcap
    elif args.task == 'diffmcq':
        eval_fn = evaluate_diffmcq
    elif args.task == 'diffrank':
        eval_fn = evaluate_diffrank

    gt_data = list(jsonlines.open(args.gt_file))
    pred_data = list(jsonlines.open(args.pred_file))

    assert len(gt_data) == len(pred_data), f'Number of gt instances ({len(gt_data)}) does not match number of predictions ({len(pred_data)})'

    results = eval_fn(gt_data, pred_data)
    print (results)