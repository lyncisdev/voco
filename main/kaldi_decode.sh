#!/usr/bin/env bash

#
# this script does the Kaldi transcription. It's probably not the fastest way to do this,
# however it's quite explicit and easy to debug.
#


. ./path.sh
. ./cmd.sh


basedir=decode

graphdir=$basedir/model/graph
data=$basedir/data/audio_records
output=$basedir/output
model=$basedir/model/final.mdl

logging=2

#################################[MFCC]###############################################

if [ $logging -le 1 ]; then
	echo " "
	echo "------- making features"
	echo " "

  START_TOTAL=$(date +%s.%N)
  START=$(date +%s.%N)

fi


compress=true
write_utt2num_frames=false

rspec="scp,p:$data/wav_sample.scp"
wspec="ark,scp:$data/feats.ark,$data/feats.scp"


 compute-mfcc-feats \
    --verbose=0 \
    --use-energy=false \
    $rspec \
    $wspec \
    &>/dev/null


# move to rspec / wspec

 compute-cmvn-stats \
    --verbose=0 \
    --spk2utt=ark:$data/spk2utt_sample \
    "scp:$data/feats.scp" \
    "ark,scp:$data/cmvn.ark,$data/cmvn.scp" \
    &>/dev/null


# move to rspec / wspec
 apply-cmvn \
    --verbose=0 \
    --utt2spk=ark:$data/utt2spk_sample \
    "scp:$data/cmvn.scp" \
    "scp:$data/feats.scp" \
    "ark,scp:$data/cmvn_mfcc.ark,$data/cmvn_mfcc.scp" \
    &>/dev/null

# move to rspec / wspec
wspec_delta="ark,scp:$data/delta_mfcc.ark,$data/delta_mfcc.scp"

 add-deltas "scp:$data/cmvn_mfcc.scp" \
    $wspec_delta \
    &>/dev/null







if [ $logging -le 1 ]; then

  END=$(date +%s.%N)
  DIFF=$(echo "$END - $START" | bc)

	echo "MFCC TIME: "
	echo $DIFF
	echo " "
	echo "------- decoding"
	echo " "


  START=$(date +%s.%N)

fi

##################################[decoding]##############################################


max_active=7000
beam=13.0
lattice_beam=6.0
acwt=0.083333 # note: only really affects pruning (scoring is on lattices).
skip_scoring=false

feats="ark,s,cs:$data/delta_mfcc.ark"



# what is thread_string?

# Generate lattices using GMM-based model
# Usage: gmm-latgen-faster \
#     [options] \
#     model-in \
#     (fst-in|fsts-rspecifier) \
#     features-rspecifier \
#     lattice-wspecifier \
#     [ words-wspecifier [alignments-wspecifier] ]

# move to rspec / wspec
 gmm-latgen-faster \
    --verbose=0 \
    --max-active=$max_active \
    --beam=$beam \
    --lattice-beam=$lattice_beam \
    --acoustic-scale=$acwt \
    --allow-partial=true \
    --word-symbol-table=$graphdir/words.txt \
    $model \
    $graphdir/HCLG.fst \
    "$feats" \
    "ark:|gzip -c > $output/lat.1.gz" \
    &>/dev/null


if [ $logging -le 1 ]; then

  END=$(date +%s.%N)
  DIFF=$(echo "$END - $START" | bc)

  echo "DECODING TIME: "
	echo $DIFF
	echo " "
	echo "------- scoring"
	echo " "

  START=$(date +%s.%N)

fi

##################################[scoring]##############################################

LMWT=20

# Generate 1-best path through lattices; output as transcriptions and alignments
# Usage: lattice-best-path [options]  <lattice-rspecifier> [ <transcriptions-wspecifier> [ <alignments-wspecifier>] ]"
# e.g.: lattice-best-path --acoustic-scale=0.1 ark:1.lats 'ark,t:|int2sym.pl -f 2- words.txt > text' ark:1.ali


# move to rspec / wspec
 lattice-best-path \
    --lm-scale=$LMWT \
    --word-symbol-table=$graphdir/words.txt \
    "ark:gunzip -c $output/lat.1.gz|" \
    "ark,t:$output/scoring/LMWT.tra" \
    &>/dev/null

# could combine lattice-best-path and following step as in the example above
# why are the allignments not being used? 

 cat $output/scoring/LMWT.tra |
	decode/scripts/int2sym.pl -f 2- $graphdir/words.txt > $output/decode_result.txt


# add decoding result to the running text file... test this
 cat $output/decode_result.txt >> $data/text


# try to estimate the lattice confidence with:
# Usage: lattice-confidence <lattice-rspecifier> <confidence-wspecifier>
# E.g.: lattice-confidence --acoustic-scale=0.08333 ark:- ark,t:-




echo | cat $output/decode_result.txt



if [ $logging -le 1 ]; then

    echo "TOTAL TIME: "
	  echo $DIFF_TOTAL

    END=$(date +%s.%N)
    DIFF=$(echo "$END - $START" | bc)
    END_TOTAL=$(date +%s.%N)
    DIFF_TOTAL=$(echo "$END_TOTAL - $START_TOTAL" | bc)

	  echo "SCORING TIME: "
	  echo $DIFF
	  echo ""
	  echo ""
fi

