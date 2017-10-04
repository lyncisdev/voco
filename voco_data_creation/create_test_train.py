import os
import shutil
import math
import random



src_dir = "audio_records/"
train_dir = "data/train/"
test_dir = "data/test/"

dirs = ["data/test", "data/train", "data/test", "data/local/dict"]



l = len(open(src_dir +'text').readlines())


for x in dirs:
	if not os.path.exists(x):
	    os.makedirs(x)

shutil.copy2(src_dir + "silence_phones.txt","data/local/dict")
shutil.copy2(src_dir + "nonsilence_phones.txt","data/local/dict")
shutil.copy2(src_dir + "optional_silence.txt","data/local/dict")
shutil.copy2(src_dir + "lexicon.txt","data/local/dict")
shutil.copy2(src_dir + "corpus.txt","data/local")


shutil.copy2(src_dir + "spk2gender","data/train")
shutil.copy2(src_dir + "spk2gender","data/test")


split_assignments = []
for x in range(0,l):
	if random.uniform(0,1) < 0.9:	
		split_assignments.append(True)
	else:
		split_assignments.append(False)


split_files = ["wav.scp","text","utt2spk"]

for f in split_files:
	
	original_file =open(src_dir + f,'r')
	train_file = open(train_dir + f, 'w')
	test_file = open(test_dir + f, 'w')
	
	for x,val in enumerate(original_file.readlines()):
					
		if split_assignments[x]:
			train_file.write(val)
		else:
			test_file.write(val)
		












