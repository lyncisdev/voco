echo
echo "===== RUNNING INITIAL SCRIPTS ====="
echo

. ./path.sh || exit 1
. ./cmd.sh || exit 1

utils/utt2spk_to_spk2utt.pl data/train/utt2spk > data/train/spk2utt
utils/utt2spk_to_spk2utt.pl data/test/utt2spk > data/test/spk2utt

echo
echo "===== FEATURES EXTRACTION ====="
echo

# Making feats.scp files
mfccdir=mfcc

# Uncomment and modify arguments in scripts below if you have any problems with data sorting
utils/validate_data_dir.sh data/train       # script for checking prepared data - here: for data/train directory
utils/fix_data_dir.sh data/train            # tool for data proper sorting if needed - here: for data/train directory
utils/validate_data_dir.sh data/test        # script for checking prepared data - here: for data/train directory
utils/fix_data_dir.sh data/test             # tool for data proper sorting if needed - here: for data/train directory

steps/make_mfcc.sh data/train exp/make_mfcc/train $mfccdir
steps/make_mfcc.sh data/test exp/make_mfcc/test $mfccdir

### dont compute cmvn!!!
steps/compute_cmvn_stats.sh data/train exp/make_mfcc/train $mfccdir
steps/compute_cmvn_stats.sh data/test exp/make_mfcc/test $mfccdir

utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang data/lang

echo
echo "===== LANGUAGE MODEL CREATION ====="
echo "===== MAKING lm.arpa ====="
echo

PATH=$PATH:$KALDI_ROOT/tools/srilm/bin/i686-ubuntu

local=data/local

mkdir $local/tmp

ngram-count -order 1 -write-vocab $local/tmp/vocab-full.txt -wbdiscount -text $local/corpus.txt -lm $local/tmp/lm.arpa

echo
echo "===== MAKING G.fst ====="
echo

lang=data/lang
arpa2fst --disambig-symbol=#0 --read-symbol-table=$lang/words.txt $local/tmp/lm.arpa $lang/G.fst

echo
echo "===== MONO TRAINING ====="
echo

steps/train_mono.sh data/train data/lang exp/mono  || exit 1

echo
echo "===== MONO DECODING ====="
echo

utils/mkgraph.sh --mono data/lang exp/mono exp/mono/graph || exit 1
steps/decode.sh --config conf/decode.config exp/mono/graph data/test exp/mono/decode

echo
echo "===== MONO ALIGNMENT ====="
echo

steps/align_si.sh data/train data/lang exp/mono exp/mono_ali || exit 1

echo
echo "===== TRI1 (first triphone pass) TRAINING ====="
echo

steps/train_deltas.sh 2000 11000 data/train data/lang exp/mono_ali exp/tri1 || exit 1

echo
echo "===== TRI1 (first triphone pass) DECODING ====="
echo

utils/mkgraph.sh data/lang exp/tri1 exp/tri1/graph || exit 1
steps/decode.sh --config conf/decode.config exp/tri1/graph data/test exp/tri1/decode

echo
echo "===== MONO ALIGNMENT ====="
echo

steps/align_si.sh data/train data/lang exp/tri1 exp/tri1_ali
utils/mkgraph.sh data/lang exp/tri1_ali exp/tri1_ali/graph

steps/decode.sh --config conf/decode.config exp/tri1_ali/graph data/test exp/tri1_ali/decode


echo
echo "===== run.sh script is finished ====="
echo



