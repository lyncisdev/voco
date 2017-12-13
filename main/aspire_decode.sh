

# online2-wav-nnet3-latgen-faster
# nnet3_rxfilename
# fst_rxfilename
# spk2utt_rspecifier
# wav_rspecifier
# clat_wspecifier


./path.sh
./cmd.sh


data=decode/data
modeldir=$KALDI_ROOT/exp/tdnn_7b_chain_online

# copy all files locally

online2-wav-nnet3-latgen-faster \
  --online=true \
  --do-endpointing=false \
  --frame-subsampling-factor=3 \
  --config=exp/tdnn_7b_chain_online/conf/online.conf \
  --max-active=7000 \
  --beam=15.0 \
  --lattice-beam=6.0 \
  --acoustic-scale=1.0 \
  --word-symbol-table=$modeldir/graph_pp/words.txt \
  $modeldir/final.mdl \
  $modeldir/graph_pp/HCLG.fst \
  'ark:$data/spk2utt_sample' \
  'scp,p:$data/wav_sample.scp' \
  'ark:/dev/null'

'
