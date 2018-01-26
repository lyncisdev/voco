#!/bin/bash


# Todo:
# make nj=1 global
# make commands generic and change directory paramters eg: tru1_ali using variables







echo
echo "===== RUNNING INITIAL SCRIPTS ====="
echo

. ./path.sh
. ./cmd.sh

utils/utt2spk_to_spk2utt.pl data/train/utt2spk > data/train/spk2utt
utils/utt2spk_to_spk2utt.pl data/test/utt2spk > data/test/spk2utt

echo
echo "===== FEATURES EXTRACTION ====="
echo

# Making feats.scp files
mfccdir=mfcc

# Uncomment and modify arguments in scripts below if you have any problems with data sorting
utils/fix_data_dir.sh data/train
utils/fix_data_dir.sh data/test

utils/validate_data_dir.sh data/train
utils/validate_data_dir.sh data/test


steps/make_mfcc.sh data/train exp/make_mfcc/train $mfccdir
steps/make_mfcc.sh data/test exp/make_mfcc/test $mfccdir

### dont compute cmvn!!!
steps/compute_cmvn_stats.sh data/train exp/make_mfcc/train $mfccdir
steps/compute_cmvn_stats.sh data/test exp/make_mfcc/test $mfccdir


# what does this do?
utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang data/lang

echo
echo "===== LANGUAGE MODEL CREATION ====="
echo "===== MAKING lm.arpa ====="
echo

# add SLIRM to the path
PATH=$PATH:$KALDI_ROOT/tools/srilm/bin/i686-m64

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

steps/train_mono.sh --nj 1 data/train data/lang exp/mono  || exit 1

echo
echo "===== MONO DECODING ====="
echo

utils/mkgraph.sh --mono data/lang exp/mono exp/mono/graph || exit 1
steps/decode.sh --nj 1 --config conf/decode.config exp/mono/graph data/test exp/mono/decode

echo
echo "===== MONO ALIGNMENT ====="
echo

steps/align_si.sh --nj 1 data/train data/lang exp/mono exp/mono_ali || exit 1

echo
echo "===== TRI1 (first triphone pass) TRAINING ====="
echo

steps/train_deltas.sh 2000 11000 data/train data/lang exp/mono_ali exp/tri1 || exit 1

echo
echo "===== TRI1 (first triphone pass) DECODING ====="
echo

utils/mkgraph.sh data/lang exp/tri1 exp/tri1/graph || exit 1
steps/decode.sh --nj 1 --config conf/decode.config exp/tri1/graph data/test exp/tri1/decode

echo
echo "===== MONO ALIGNMENT ====="
echo

steps/align_si.sh --nj 1 data/train data/lang exp/tri1 exp/tri1_ali
utils/mkgraph.sh data/lang exp/tri1_ali exp/tri1_ali/graph || exit 1

graphdir=exp/tri1_ali/graph
data=data/test
dir=exp/tri1_ali/decode

steps/decode.sh --nj 1 --config conf/decode.config $graphdir $data $dir


# remove $scoring_opts

local/score.sh $scoring_opts $data $graphdir $dir "UNK" "SIL"

# cat wer result 

# compute-wer
# Compute WER by comparing different transcriptions
# Takes two transcription files, in integer or text format,
# and outputs overall WER statistics to standard output.

# Usage: compute-wer [options] <ref-rspecifier> <hyp-rspecifier>
# E.g.: compute-wer --text --mode=present ark:data/train/text ark:hyp_text
# See also: align-text,
# Example scoring script: egs/wsj/s5/steps/score_kaldi.sh


echo
echo "===== run.sh script is finished ====="
echo



