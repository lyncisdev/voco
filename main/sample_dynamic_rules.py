
import os
import pprint
import json
import random
import time
# from collections import defaultdict

from parser import parser,implementation

basedir = "parser/"
dynamic_rules_file = open(basedir + "dynamic_rules_final.json", "r")
dynamic_rules = json.load(dynamic_rules_file)
dynamic_rules_file.close()

'''Create randomly sampled recording list'''


recording_list_file = open('recording_list.txt', 'w')

rule = "EMACS_LINE_ACTIONS"
rule = "I3WM"
rule = "SWITCH_APPLICATION"
pprint.pprint(dynamic_rules[rule])

for count in range(0,50):
    tmp = ""
    for var in dynamic_rules[rule]["SIGNATURE"]:
        tmp += random.choice(list(dynamic_rules[rule]["VARIABLES"][var].keys()))
        tmp += " "


    recording_list_file.write(str(count).zfill(3) + "," + tmp + "\n")

'''check coverage in live'''
try:
    voco_data_base = os.environ['VOCO_DATA']
    print(os.environ['VOCO_DATA'])
except:
    print('VOCO_DATA not defined')


dynamic_rules,static_rules, var_lookup = parser.init()

text = open(voco_data_base + "/staging/audio_records/text","r")
lines = text.readlines()

print(len(lines))

phrase_dict = {}

for line in lines:
    try:
        UID, phrase = line.strip().split(" ",1)
    except ValueError as e:
        # this error occurs if Kaldi did not manage to transcribe anything
        UID, phrase = "000",""

    commands,matches = parser.parsephrase(dynamic_rules,static_rules,var_lookup,phrase,"",ignore_context=True)


    # print(len(matches))

    if len(matches) == 1:
        for match in matches:
            if match[0] == rule:
                # print(phrase)
                # print(matches)
                if phrase not in phrase_dict:
                    phrase_dict[phrase] = []

                phrase_dict[phrase].append(UID)

pprint.pprint(phrase_dict)

for phrase in phrase_dict:

    print("%s - %i" % (phrase, len(phrase_dict[phrase])))
    input("")
    for x,UID in enumerate(phrase_dict[phrase]):
        wav_file = voco_data_base + "/staging/audio_data/" + UID + ".wav"
        print(x)
        os.system("aplay " + wav_file)
        time.sleep(0.3)
        if x % 10 == 0:
            input("")
    input("")

# live_samples = voco_data_base + "/staging/audio_data"

# # from os import listdir
# # from os.path import isfile, join

# live_samples_files = [f for f in os.listdir(live_samples) if os.path.isfile(os.path.join(live_samples, f))]

# print(len(live_samples_files))

# for sample in live_samples_files:

#     # Run Kaldi, the script decodes for your sample and saves the transcription to a text file.
#     result = subprocess.check_output("./kaldi_decode.sh").strip().decode('UTF-8')

#     try:
#         result = result.split(" ", 1)[1].strip()
#     except IndexError as e:
#         # this error occurs if Kaldi did not manage to transcribe anything
#         result = ""


#     commands, matches = parser.parsephrase(dynamic_rules, static_rules, var_lookup,line, "",ignore_context=False)
