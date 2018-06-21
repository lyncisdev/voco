
import os
import pprint
import json
import random
import time
# from collections import defaultdict

from parser import parser,implementation

# basedir = "parser/"
# dynamic_rules_file = open(basedir + "dynamic_rules_final.json", "r")
# dynamic_rules = json.load(dynamic_rules_file)
# dynamic_rules_file.close()

# '''Create randomly sampled recording list'''


dynamic_rules, static_rules, var_lookup = parser.init()

correct = "N"


while correct != "Y":

    index = 0
    for rule in dynamic_rules:
        print("%0.2i - %s - DYNAMIC" % (index, rule.ljust(40)))
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


    print("Chosen: %s - %s" % (chosen_rule, rule_type))


    correct = input("Correct? Y/N").upper()

rule = chosen_rule

recording_list_file = open('recording_list.txt', 'w')

# rule = "EMACS_LINE_ACTIONS"
# rule = "I3WM"
# rule = "SWITCH_APPLICATION"
# pprint.pprint(dynamic_rules[rule])

for count in range(0,50):
    tmp = ""
    for var in dynamic_rules[rule]["SIGNATURE"]:
        tmp += random.choice(list(dynamic_rules[rule]["VARIABLES"][var].keys()))
        tmp += " "


    recording_list_file.write(str(count).zfill(3) + "," + tmp + "\n")
