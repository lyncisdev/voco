#!/usr/bin/env bash



. ./path.sh
. ./cmd.sh

# cd kaldi/egs/aspire/s5


# online2-wav-nnet3-latgen-faster
# nnet3_rxfilename
# fst_rxfilename
# spk2utt_rspecifier
# wav_rspecifier
# clat_wspecifier


# exp/tdnn_7b_chain_online/conf/online.conf

data=aspire
# modeldir=$KALDI_ROOT/exp/tdnn_7b_chain_online
modeldir=$KALDI_ROOT/egs/aspire/s5/exp/tdnn_7b_chain_online
# copy all files locally

online2-wav-nnet3-latgen-faster \
  --online=true \
  --do-endpointing=false \
  --frame-subsampling-factor=3 \
  --config=$modeldir/conf/online.conf \
  --max-active=7000 \
  --beam=15.0 \
  --lattice-beam=6.0 \
  --acoustic-scale=1.0 \
  --word-symbol-table=$modeldir/graph_pp/words.txt \
  $modeldir/final.mdl \
  $modeldir/graph_pp/HCLG.fst \
  'ark:echo utterance-id1 utterance-id1|' \
  'scp:echo utterance-id1 aspire/test8k.wav|' \
  'ark:/dev/null'
