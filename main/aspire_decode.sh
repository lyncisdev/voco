#!/usr/bin/env bash



. ./path.sh
. ./cmd.sh




# online2-wav-nnet3-latgen-faster
# nnet3_rxfilename
# fst_rxfilename
# spk2utt_rspecifier
# wav_rspecifier
# clat_wspecifier




data=aspire
# modeldir=$KALDI_ROOT/exp/tdnn_7b_chain_online
modeldir=$KALDI_ROOT/egs/wsj/s5/steps/nnet3/tdnn
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
  'scp:echo utterance-id1 $data/test8k.wav|' \
  'ark:/dev/null'
