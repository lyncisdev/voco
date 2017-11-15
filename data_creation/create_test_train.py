import os
import shutil
import math
import random
import sys

try:
    base_directory = sys.argv[1]
#    print(base_directory)
except:
    print('Please pass voco_data base directory')

src_dir = base_directory + "/audio_records/"
train_dir = base_directory +"/data/train/"
test_dir = base_directory + "/data/test/"
local_dir = base_directory + "/data/local/"

dirs = [train_dir, test_dir, local_dir, local_dir + "dict"]

for x in dirs:
    if not os.path.exists(x):
        os.makedirs(x)

        

        
shutil.copy2(src_dir + "silence_phones.txt",local_dir + "dict")
shutil.copy2(src_dir + "nonsilence_phones.txt",local_dir + "dict")
shutil.copy2(src_dir + "optional_silence.txt",local_dir + "dict")
shutil.copy2(src_dir + "lexicon.txt",local_dir + "dict")
shutil.copy2(src_dir + "corpus.txt",local_dir)


shutil.copy2(src_dir + "spk2gender",train_dir)
shutil.copy2(src_dir + "spk2gender",test_dir)


split_assignments = []
l = len(open(src_dir +'text').readlines())



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
		












