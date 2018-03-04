#!/usr/bin/python

#
# create_test_train.py
#
# takes the records in VOCO_DATA/audio_records and creates VOCO_DATA/data directory in the Kaldi required format.
# Also splits the data into training (90% of records) and testing (10%) datasets.

import os
import shutil
import math
import random
import sys
import csv
import pprint
print(os.environ['VOCO_DATA'])

try:
    voco_data_base = os.environ['VOCO_DATA']
except:
    print('VOCO_DATA not defined')

src_dir = voco_data_base + "/audio_records/"
train_dir = voco_data_base + "/data/train/"
test_dir = voco_data_base + "/data/test/"
local_dir = voco_data_base + "/data/local/"

dirs = [train_dir, test_dir, local_dir, local_dir + "dict"]

for x in dirs:
    if not os.path.exists(x):
        os.makedirs(x)

shutil.copy2(src_dir + "silence_phones.txt", local_dir + "dict")
shutil.copy2(src_dir + "nonsilence_phones.txt", local_dir + "dict")
shutil.copy2(src_dir + "optional_silence.txt", local_dir + "dict")
shutil.copy2(src_dir + "lexicon.txt", local_dir + "dict")
shutil.copy2(src_dir + "corpus.txt", local_dir)

shutil.copy2(src_dir + "spk2gender", train_dir)
shutil.copy2(src_dir + "spk2gender", test_dir)

# original_file = open(src_dir + "wav.scp", 'r')
with open(src_dir + "wav.scp", 'r') as wavfile:
    reader = csv.reader(wavfile, delimiter=' ')
    WAV = list(reader)

UID = []
for line in WAV:
    UID.append(line[0])

order = [i[0] for i in sorted(enumerate(UID), key=lambda x: x[1])]

print("Order: %d" % len(order))

# pp = pprint.PrettyPrinter(depth=4, width=5)
# pp.pprint(UID)

split_assignments = []
l = len(order)

num_test = 0
num_train = 0

for x in range(0, l):
    if random.uniform(0, 1) < 0.9:
        num_train += 1
        split_assignments.append(True)
    else:
        num_test += 1
        split_assignments.append(False)

split_files = ["wav.scp", "text", "utt2spk"]

for f in split_files:

    print(src_dir + f)
    original_file = open(src_dir + f, 'r')
    train_file = open(train_dir + f, 'w')
    test_file = open(test_dir + f, 'w')

    lines = original_file.readlines()

    print("%s - %d" % (f, len(lines)))

    for x in range(0,l):

        if split_assignments[x]:
            train_file.write(lines[order[x]])
        else:
            test_file.write(lines[order[x]])

print("Total:%i | Train: %i | Test: %i" % (l, num_train, num_test))
