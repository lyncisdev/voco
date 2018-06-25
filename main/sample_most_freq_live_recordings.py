import os
import pprint
import random
import shutil
from parser import parser, implementation

from collections import OrderedDict
from operator import itemgetter    
try:
    voco_data_base = os.environ['VOCO_DATA']
    print(os.environ['VOCO_DATA'])
except:
    print('VOCO_DATA not defined')

text = open(voco_data_base + "/staging/audio_records/text", "r")
lines = text.readlines()

reviewed = open('reviewed.txt', 'r')
tmp_reviewed = reviewed.readlines()

reviewed = []
for tmp in tmp_reviewed:
    reviewed.append(tmp.strip())
# pprint.pprint(reviewed, width=200, indent=4)

ignore_phrases = []
with open("static_freq.txt", "r") as f:
    static_freq = f.readlines()

for line in static_freq:
    phrase, freq = line.split(",", 1)
    if int(freq) > 50:
        ignore_phrases.append(phrase)

# pprint.pprint(ignore_phrases, width=200, indent=4)

missing = []

# Remove entries from text and wav where there is no associated file
for line in lines:

    tokens = line.strip().split(" ", 1)
    UID = tokens[0]
    audio_sample_file_path = voco_data_base + "/staging/audio_data/" + UID + ".wav"
    if not os.path.isfile(audio_sample_file_path):
        # print(UID)
        missing.append(UID)

# input("Done printing missing files")

dynamic_rules, static_rules, var_lookup = parser.init()


UIDS = {}
print(len(lines))
for line in lines:

    tokens = line.strip().split(" ", 1)

    if len(tokens) > 1:
        UID = tokens[0]
        phrase = tokens[1]

        phrase_len = len(phrase.split(" "))

        commands, matches = parser.parsephrase(
            dynamic_rules,
            static_rules,
            var_lookup,
            phrase,
            "",
        ignore_context=True)

        if len(matches) > 0:
            if (UID not in missing) and (UID not in reviewed) and (phrase_len > 1):
                if (phrase not in UIDS):
                    UIDS[phrase] = []

                UIDS[phrase].append(UID)


# pprint.pprint(UIDS, width=200, indent=4)

tmp_UIDS = UIDS.copy()
for phrase in UIDS:
    if len(UIDS[phrase]) < 10:
        tmp_UIDS.pop(phrase)

UIDS = tmp_UIDS

UIDS = OrderedDict(sorted(UIDS.items(), key=itemgetter(0)))

group_size = 5

def audio_move(voco_data_base, UID, phrase):

    audio_data_directory = voco_data_base + "/audio_data/"
    audio_records_directory = voco_data_base + "/audio_records/"
    audio_sample_file_path = voco_data_base + "/staging/audio_data/" + UID + ".wav"

    shutil.move(audio_sample_file_path, audio_data_directory + UID + ".wav")

    outputfile = open(audio_records_directory + 'wav.scp', 'a')
    outputfile.write(UID + " " + audio_data_directory + UID + ".wav" + "\n")

    outputfile = open(audio_records_directory + "text", 'a')
    outputfile.write(UID + " " + phrase + "\n")

    outputfile = open(audio_records_directory + 'utt2spk', 'a')
    outputfile.write(UID + " bartek" + "\n")


while True:

    index = 0
    for phrase in UIDS:
        print("%0.2i - %s - %i" % (index, phrase.ljust(40), len(UIDS[phrase])))
        index += 1

    phrase_num = int(input("Choose phase:"))
    chosen_phrase = "none"

    index = 0
    for phrase in UIDS:
        if phrase_num == index:
            chosen_phrase = phrase
        index += 1


    phrase = chosen_phrase


    if len(UIDS[phrase]) < group_size:
        continue

    if phrase in ignore_phrases:
        continue

    tmp_uids = []
    c = 0

    print("\n\n\n%s\n\n\n" % (phrase))

    for UID in UIDS[phrase]:

        if UID not in missing:
            c += 1

            audio_sample_file_path = voco_data_base + "/staging/audio_data/" + UID + ".wav"
            os.system("aplay " + audio_sample_file_path)

            tmp_uids.append(UID)

            if c % group_size == 0:
                accept = input("\naccept (y)")

                if accept == "y":
                    for tmp in tmp_uids:
                        print(tmp)
                        audio_move(voco_data_base, tmp, phrase)

                    print("Accepted")
                else:
                    print("Rejected")

                for tmp in tmp_uids:
                    with open("reviewed.txt", "a") as f:
                        f.write("%s\n" % tmp)

                tmp_uids = []
                c = 0

        else:
            print("missing -%s" % UID)

