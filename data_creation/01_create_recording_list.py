#!/usr/bin/python



# inputs
#	utt_list
#	n - number of repeats
# output
# 	recording_list in the format of utt_list wiht

import re
import random
import subprocess
import pprint

################[INPUTS]################

command_file = open('commands.csv', 'r')

recording_list_file = open('recording_list.txt', 'w')

# load tree

commands = command_file.readlines()

unmixed_command_list = []
mixed_command_list = []

#Final,Frequency,Group

for x in commands[1:]:
    parts = re.split(r',', x)

    phrase = parts[0]
    freq = int(parts[1])
    group = int(parts[2])

    if group == 0:
        for x in range(1, freq):
            unmixed_command_list.append(phrase)
    else:
        for x in range(1, freq):
            mixed_command_list.append(phrase)

#print(mixed_command_list)
#print(unmixed_command_list)

recording_list = []

# for x in range(0,1):
# i = random.randint(0,len(unmixed_command_list)-1)
# recording_list.append(unmixed_command_list[i])

for x in range(0, 40):
    tmp = ""
    for y in range(0, random.randint(2, 5)):
        i = random.randint(0, len(mixed_command_list) - 1)

        tmp += mixed_command_list[i]
        tmp += " "

    recording_list.append(tmp)

count = 0
for x in recording_list:
    recording_list_file.write(str(count).zfill(3) + "," + x + "\n")
    count += 1
