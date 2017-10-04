#
# inputs
#	utt_list
#	n - number of repeats
# output
# 	recording_list in the format of utt_list wiht


import re
from random import randint
import subprocess

################[INPUTS]################

utt_list_file = open('utt_list.txt','r')

recording_list_file = open('recording_list.txt', 'w')

n = 2;

################[CODE]################

utt_list = utt_list_file.readlines()

new_utt_list = []

for x in utt_list:
	if x[0]!="#":
		new_utt_list.append(x)

utt_list = new_utt_list

num_utt = len(utt_list)
num_samples = num_utt * n

for x in range(0,num_samples):
	i = randint(0, num_utt-1)
	recording_list_file.write(utt_list[i])





