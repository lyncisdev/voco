

#
# Check coverage
#
import os
import parser
import pprint

try:
    voco_data_base = os.environ['VOCO_DATA']
    print(os.environ['VOCO_DATA'])
except:
    print('VOCO_DATA not defined')


text = open(voco_data_base + "/audio_records/text","r")

lines = text.readlines()

rules, var_lookup = parser.init()

rule_freq = {}

for rule in rules:
    rule_freq[rule] = {}

    sig = rules[rule]["SIGNATURE"]
    for var in sig:
        for elem in rules[rule]["VARIABLES"][var]:
            rule_freq[rule][elem] = 0



for line in lines:
    phrase = line.strip().split(" ",1)[1]
    print(phrase)

    cmd, matches = parser.parsephrase(rules, var_lookup,phrase,"")
    if len(matches) > 0:

        for match in matches:

            print(match)
            for elem in match[1]:
                rule_freq[match[0]][elem[1]] += 1


pp = pprint.PrettyPrinter(depth=4, width=5)
pp.pprint(rule_freq)

