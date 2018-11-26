
import os
import pprint
import random
from parser import parser,implementation

dynamic_rules,static_rules, var_lookup = parser.init()


recording_list_file = open('recording_list.txt', 'w')

correct = "N"

while correct != "Y":

    index = 0
    for rule in static_rules:
        print("%i - %s - STATIC" % (index, rule.ljust(40)))
        index += 1

    rule_num = int(input("Choose rule:"))
    chosen_rule = "none"
    rule_type = "none"

    index = 0
    for rule in static_rules:
        if rule_num == index:
            chosen_rule = rule
            rule_type = "static"
        index += 1

    print("Chosen: %s - %s" % (chosen_rule, rule_type))


    correct = input("Correct? Y/N").upper()

rule = chosen_rule


for count in range(0,50):
    tmp = random.choice(list(static_rules[rule]["RULES"].keys()))

    recording_list_file.write(str(count).zfill(3) + "," + tmp + "\n")

with open("../data_creation/recording_list_counter.txt", "w") as f:
        f.write(str("0"))
