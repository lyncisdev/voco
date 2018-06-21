import os
import pprint
import random
import shutil
from parser import parser, implementation

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

correct = "N"


# correct = "Y"
# rule_type = "dynamic"
# chosen_rule = "EMACS_JUMP_LINE_3"
# chosen_rule = "MODIFIER_SINGLE"

while correct != "Y":

    index = 0
    for rule in dynamic_rules:
        print("%0.2i - %s - DYNAMIC" % (index, rule.ljust(40)))
        index += 1

    for rule in static_rules:
        print("%i - %s - STATIC" % (index, rule.ljust(40)))
        index += 1

    rule_num = int(input("Choose rule:"))
    chosen_rule = "none"
    rule_type = "none"

    index = 0
    for rule in dynamic_rules:
        if rule_num == index:
            chosen_rule = rule
            rule_type = "dynamic"
        index += 1

    for rule in static_rules:
        if rule_num == index:
            chosen_rule = rule
            rule_type = "static"
        index += 1

    print("Chosen: %s - %s" % (chosen_rule, rule_type))


    correct = input("Correct? Y/N").upper()

rule = chosen_rule


# rule = "STATIC_EMACS_KEYS"
# rule = "STATIC_PAUSE"
# rule = "STATIC_EMACS_BUFFER_FUNCTIONS"
# rule = "STATIC_TERMINAL_TYPE_RETURN"
# # rule = "STATIC_TERMINAL_TYPE"
# # rule = "STATIC_FIREFOX_KEYS"

if rule_type == "static":
    pprint.pprint(static_rules[rule]["RULES"].keys(), width=200, indent=4)

elif rule_type == "dynamic":
    pprint.pprint(dynamic_rules[rule]["SIGNATURE"], width=200, indent=4)

UIDS = {}

for line in lines:

    tokens = line.strip().split(" ", 1)

    if len(tokens) > 1:

        UID = tokens[0]
        phrase = tokens[1]
        commands, matches = parser.parsephrase(
            dynamic_rules,
            static_rules,
            var_lookup,
            phrase,
            "",
            ignore_context=True,
            all_matches=True)

        if len(matches) > 0:
            for match in matches:
                if match[0] == rule:
                    if rule_type == "static":
                        if (UID not in missing) and (
                                phrase in static_rules[rule]["RULES"].keys()) and (
                                    UID not in reviewed):

                            if (phrase not in UIDS):
                                UIDS[phrase] = []

                            UIDS[phrase].append(UID)
                            break

                    elif rule_type == "dynamic":


                        if (UID not in missing) and (len(phrase.split(" ")) == len(match[1])) and (
                                    UID not in reviewed):
                            if (phrase not in UIDS):
                                UIDS[phrase] = []

                            UIDS[phrase].append(UID)
                            break

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



if rule_type == "static":
    group_size = 5

elif rule_type == "dynamic":
    group_size = 5




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

    # accept = input("\naccept (y)")

    # if accept == "y":
    #     for tmp in tmp_uids:
    #         print(tmp)
    #         audio_move(voco_data_base, tmp, phrase)
    #     print("Accepted")
    # else:
    #     print("Rejected")

    # for tmp in tmp_uids:
    #     with open("reviewed.txt", "a") as f:
    #         f.write("%s\n" % tmp)

    # tmp_uids = []
    # c = 0
