
./path.sh
./cmd.sh

graphdir=decode/model/graph
data=decode/data
dir=decode/output

stage=0
logging=5

#################################[MFCC]###############################################
if [ $logging -le 1 ]; then
	echo " "
	echo "------- making features"
	echo " "
fi

START_TOTAL=$(date +%s.%N)
START=$(date +%s.%N)

compress=true

write_utt2num_frames=false  # if true writes utt2num_frames <- most fucking useless comment ever

rspec="scp,p:$data/wav_sample.scp"
wspec="ark,scp:$data/feats.ark,$data/feats.scp"
compute-mfcc-feats --verbose=0 --use-energy=false $rspec $wspec &>/dev/null

compute-cmvn-stats --verbose=0 --spk2utt=ark:$data/spk2utt_sample scp:$data/feats.scp ark,scp:$data/cmvn.ark,$data/cmvn.scp &>/dev/null


wspec_delta="ark,scp:$data/delta_mfcc.ark,$data/delta_mfcc.scp"
apply-cmvn \
    --verbose=0 \
    --utt2spk=ark:$data/utt2spk_sample \
    "scp:$data/cmvn.scp" \
    "scp:$data/feats.scp" \
    "ark,scp:$data/cmvn_mfcc.ark,$data/cmvn_mfcc.scp" \
    &>/dev/null

add-deltas "scp:$data/cmvn_mfcc.scp" \
    $wspec_delta \
    &>/dev/null


END=$(date +%s.%N)
DIFF=$(echo "$END - $START" | bc)

if [ $logging -le 1 ]; then
	echo "MFCC TIME: "
	echo $DIFF
	echo " "
	echo "------- decoding"
	echo " "
fi

##################################[decoding]##############################################
START=$(date +%s.%N)


max_active=7000
beam=13.0
lattice_beam=6.0
acwt=0.083333 # note: only really affects pruning (scoring is on lattices).
skip_scoring=false


srcdir=decode/model; # The model directory is one level up from decoding directory.

model=$srcdir/final.mdl

feats="ark,s,cs:$data/delta_mfcc.ark"

gmm-latgen-faster$thread_string\
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
    "ark:|gzip -c > $dir/lat.1.gz" \
    &>/dev/null 


END=$(date +%s.%N)
DIFF=$(echo "$END - $START" | bc)

if [ $logging -le 1 ]; then
	echo "DECODING TIME: "
	echo $DIFF
	echo " "
	echo "------- scoring"
	echo " "
fi

##################################[scoring]##############################################


START=$(date +%s.%N)

LMWT=20

lattice-best-path \
    --lm-scale=$LMWT \
    --word-symbol-table=$graphdir/words.txt \
    "ark:gunzip -c $dir/lat.1.gz|" \
    ark,t:$dir/scoring/LMWT.tra \
    &>/dev/null 



cat $dir/scoring/LMWT.tra |
	decode/scripts/int2sym.pl -f 2- $graphdir/words.txt > $dir/decode_result.txt

END=$(date +%s.%N)
DIFF=$(echo "$END - $START" | bc)
END_TOTAL=$(date +%s.%N)
DIFF_TOTAL=$(echo "$END_TOTAL - $START_TOTAL" | bc)


if [ $logging -le 1 ]; then
	echo "SCORING TIME: "
	echo $DIFF
	echo ""
	echo ""

fi

if [ $logging -le 2 ]; then

	echo "TOTAL TIME: "
	echo $DIFF_TOTAL

fi

cat $dir/decode_result.txt >> $data/text


#echo ""
#echo "Output"
echo | cat $dir/decode_result.txt

### stop execution
#if [ $stage -le 1 ]; then
#fi

