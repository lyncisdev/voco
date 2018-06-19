#
# Check coverage
#



import os
import pprint
from random import shuffle
from parser import parser,implementation

try:
    voco_data_base = os.environ['VOCO_DATA']
    print(os.environ['VOCO_DATA'])
except:
    print('VOCO_DATA not defined')


text = open(voco_data_base + "/audio_records/text","r")

lines = text.readlines()

dynamic_rules,static_rules, var_lookup = parser.init()

rule_freq = {}
rule_UID = {}
for rule in static_rules:


    for sig in static_rules[rule]["RULES"]: 
        # print(sig)
        rule_UID[sig] = []
        rule_freq[sig] = 0

# for rule in dynamic_rules:
#     rule_freq[rule] = {}
#     # for sig in dynamic_rules[rule]["SIGNATURE"]: 
#         rule_freq[rule][sig] = 0


# pp = pprint.PrettyPrinter(depth=4, width=100)
# pp.pprint(rule_freq)

passed_parser = set()

for line in lines:
    UID, phrase = line.strip().split(" ",1)


    commands,matches = parser.parsephrase(dynamic_rules,static_rules,var_lookup,phrase,"",ignore_context=True)


    print(phrase)
    print(len(matches))
    if len(matches) > 0:

        for match in matches:
            tmp = ""
            for elem in match[1]:
                tmp += elem[1]
                tmp += " "
            tmp = tmp.strip()
            if tmp in rule_freq:
                rule_UID[tmp].append(UID)
                rule_freq[tmp] += 1
        passed_parser.add(UID)


print("Rule Freq")
pp = pprint.PrettyPrinter(depth=4, width=5)
pp.pprint(rule_freq)


print("Passed parser %i" % len(passed_parser))
print("Total %i" % len(lines) )


update_recoding_list =  True 

if update_recoding_list:

    rules_to_sample = []

    for rule in rule_freq:
        if rule_freq[rule] < 20:
            rules_to_sample.append(rule)

    recording_list_file = open('recording_list.txt', 'w')

    # rules_to_sample.append("evaluate")
    # rules_to_sample.append("complete")

    count = 0

    for j in range(0,8):
        shuffle(rules_to_sample)
        for x in rules_to_sample:
            recording_list_file.write(str(count).zfill(3) + "," + x + "\n")
            count += 1
