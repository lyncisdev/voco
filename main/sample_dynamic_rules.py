
import pprint
import json
import random

basedir = "parser/"
dynamic_rules_file = open(basedir + "dynamic_rules_final.json", "r")
dynamic_rules = json.load(dynamic_rules_file)
dynamic_rules_file.close()


recording_list_file = open('recording_list.txt', 'w')

rule = "EMACS_LINE_ACTIONS"
rule = "I3WM"
pprint.pprint(dynamic_rules[rule])

for count in range(0,50):
    tmp = ""
    for var in dynamic_rules[rule]["SIGNATURE"]:
        tmp += random.choice(list(dynamic_rules[rule]["VARIABLES"][var].keys()))
        tmp += " "


    recording_list_file.write(str(count).zfill(3) + "," + tmp + "\n")
