

# online2-wav-nnet3-latgen-faster
# nnet3_rxfilename
# fst_rxfilename
# spk2utt_rspecifier
# wav_rspecifier
# clat_wspecifier




./path.sh
./cmd.sh


export KALDI_ROOT=~/Projects/ASR/kaldi_mar_17
export PATH=$KALDI_ROOT/src/online2bin:$PATH

data=decode/data
modeldir=$KALDI_ROOT/egs/aspire/s5/exp/tdnn_7b_chain_online

# copy all files locally

ffmpeg -i dictate.wav -acodec pcm_s16le -ac 1 -ar 8000 dictate8k.wav


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
  'scp:echo utterance-id1 dictate8k.wav|' \
  'ark:/dev/null'

