
import os
import pprint
import random
from parser import parser,implementation

dynamic_rules,static_rules, var_lookup = parser.init()


recording_list_file = open('recording_list.txt', 'w')

rule = "STATIC_EMACS_KEYS"
rule = "STATIC_PAUSE"
rule = "STATIC_TERMINAL_TYPE"
rule = "STATIC_FIREFOX_KEYS"

pprint.pprint(static_rules[rule])

for count in range(0,50):
    tmp = random.choice(list(static_rules[rule]["RULES"].keys()))

    recording_list_file.write(str(count).zfill(3) + "," + tmp + "\n")

with open("../data_creation/recording_list_counter.txt", "w") as f:
        f.write(str("0"))
