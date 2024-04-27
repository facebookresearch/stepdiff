#  Copyright (c) Meta Platforms, Inc. and affiliates.
#  All rights reserved.
#
#  This source code is licensed under the license found in the
#  LICENSE file in the root directory of this source tree.

mkdir -p predictions/
wget https://dl.fbaipublicfiles.com/stepdiff/predictions/stepdiff_diffcap_preds.jsonl -P predictions/
wget https://dl.fbaipublicfiles.com/stepdiff/predictions/stepdiff_diffmcq_preds.jsonl -P predictions/
wget https://dl.fbaipublicfiles.com/stepdiff/predictions/stepdiff_diffrank_preds.jsonl -P predictions/