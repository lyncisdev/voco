nj=1
cmd=run.pl
mfcc_config=conf/mfcc.conf


# make this false!!!!!! try uncompressed features
compress=true

write_utt2num_frames=false  # if true writes utt2num_frames <- most fucking useless comment ever

data=$1
if [ $# -ge 2 ]; then
  logdir=$2
else
  logdir=$data/log
fi
if [ $# -ge 3 ]; then
  mfccdir=$3
else
  mfccdir=$data/data
fi

# make $mfccdir an absolute pathname.
mfccdir=`perl -e '($dir,$pwd)= @ARGV; if($dir!~m:^/:) { $dir = "$pwd/$dir"; } print $dir; ' $mfccdir ${PWD}`

# use "name" as part of name of the archive.
name=`basename $data`

mkdir -p $mfccdir || exit 1;
mkdir -p $logdir || exit 1;


scp=$data/wav.scp
write_num_frames_opt=

split_scps="$split_scps $logdir/wav_${name}.1.scp"


utils/split_scp.pl $scp $split_scps || exit 1;

########## the actual MFCC code!!!!!!!!!!
  $cmd JOB=1:$nj $logdir/make_mfcc_${name}.JOB.log \
    compute-mfcc-feats  $vtln_opts --verbose=2 --config=$mfcc_config \
     scp,p:$logdir/wav_${name}.JOB.scp ark:- \| \
      copy-feats $write_num_frames_opt --compress=$compress ark:- \
      ark,scp:$mfccdir/raw_mfcc_$name.JOB.ark,$mfccdir/raw_mfcc_$name.JOB.scp \
      || exit 1;

# concatenate the .scp files together.
for n in $(seq $nj); do
  cat $mfccdir/raw_mfcc_$name.$n.scp || exit 1;
done > $data/feats.scp || exit 1


rm $logdir/wav_${name}.*.scp  $logdir/segments.* 2>/dev/null


echo "Succeeded creating MFCC features for $name"
