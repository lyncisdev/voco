#
# Parser unit test
#

import pprint
import json
import subprocess
from implementation import *
import re
pp = pprint.PrettyPrinter(depth=4, width=5)


phrases = [
    "open nautilus", "open nautilus here", "open firefox", "close browser",
    "switch to firefox", "open max", "show firefox", "open terminal",
    "type alpha"
]

phrases = ["alpha","alpha charlie","alpha charlie three firefox","alpha charlie three open firefox"]
phrases = ["sky alpha charlie three open"]
# phrases = ["alpha"]

#
# Load rules file
#

rules_file = open("rules.json", "r")
rules = json.load(rules_file)
rules_file.close()


variables_file = open("variables.json", "r")
variables = json.load(variables_file)
variables_file.close()

# Add a blank rule with the correct format
# rule = {}
# rule["NAME"] = "DEFAULT"
# rule["SIGNATURE"] = "[VAR1][VAR2]"
# rule["LENGTH"] = 2
# rule["CONTEXT"] = "ALL"
# rule["VARIABLES"] = {}
# rule["VARIABLES"]["VAR1"] = {"opt1": "opt1"}
# rule["VARIABLES"]["VAR2"] = {"opt1": "opt1"}

# if rule["NAME"] not in rules:
#     rules[rule["NAME"]] = rule

# rules_file = open("rules.json", "w")
# json.dump(rules, rules_file)
# rules_file.close()

#####################################################
# insert repeated variables
#####################################################


for rule in rules:
    for var in rules[rule]["VARIABLES"]:

        val = rules[rule]["VARIABLES"][var]
        if not isinstance(val,dict):
            if val in variables:
                rules[rule]["VARIABLES"][var] = variables[val]
            else:
                print("error")
#####################################################
# Pre-compile rules
#####################################################

var_lookup = {}

for rule in rules:

    for var in rules[rule]["SIGNATURE"]:
        for word in rules[rule]["VARIABLES"][var]:
            if word not in var_lookup:
                var_lookup[word] = []

            var_lookup[word].append([rule, var])

rules_lookup_file = open("rules_lookup.json", "w")
json.dump(var_lookup, rules_lookup_file)

#####################################################
# test rules on phrases 
#####################################################


for phrase in phrases:
    print("\n------------------------\n%s\n------------------------" % phrase)

    rule_opt = {}

    words = phrase.split()
    phrase_lenght = len(words)




    graph = []
    for word in words:
        graph.append([word,[]])

    rule_graph = {}

    for c,word in enumerate(words):
        if word in var_lookup:
            for keyword in var_lookup[word]:

                rule = keyword[0]
                var = keyword[1]

                if rule not in rule_graph:
                    rule_graph[rule] = []

                rule_graph[rule].append([var, word, c])


    # Remove rules that don't fit
    new_rule_graph = {}

    for rule in rule_graph:
        if len(rule_graph[rule]) >= rules[rule]["LENGTH"]:
            new_rule_graph[rule] = rule_graph[rule]

    rule_graph = new_rule_graph

    # pp.pprint(rule_graph)

    matches = []
    # print candidates

    for rule in rule_graph:

        # print(rules[rule]["SIGNATURE"])
        # print(rule_graph[rule])

        # match rules by comparing signatures

        l = rules[rule]["LENGTH"]

        for x in range(0,len(rule_graph[rule])-l+1):
            match = True

            # print(x+l)
            sig = rules[rule]["SIGNATURE"]
            subarr = rule_graph[rule][x:x+l]
            # print(sig)
            # print(subarr)


            for y in range(0,l):
                if sig[y] != subarr[y][0]:
                    match = False

            if match == True:
                matches.append([rule,subarr])

    for match in matches:
        print(match)


    print("\n\n")
    #
    # Build set representation
    #

    match_set = {}
    for x,match in enumerate(matches):
        tmp = set()
        for elem in match[1]:
            tmp.add(elem[2])

        match_set[x] = tmp

    #
    # try set cover solution
    #
    final_match = []

    while len(match_set) > 0:
        # find largest uncovered set

        m = 0
        pos = -1
        for x in match_set:
            if len(match_set[x]) > m:
                m = len(match_set[x])
                pos = x

        final_match.append(matches[pos])

        #
        # remove overlaps
        #
        new_match_set = {}
        for x in match_set:
            if len(set.intersection(match_set[pos],match_set[x])) == 0:
                new_match_set[x] = match_set[x]
        match_set = new_match_set

    # convert to dict

    new_final_match = []

    for match in final_match:
        tmp_dict = {}
        for elem in match[1]:
            lookupval = rules[match[0]]["VARIABLES"][elem[0]][elem[1]]
            tmp_dict[elem[0]] = [elem[1],lookupval]
        tmp = [match[0], tmp_dict]
        new_final_match.append(tmp)

    final_match = new_final_match

    # # execute command
    # for match in final_match:

    #     res = locals()[rules[match[0]]["FUNCTION"]](match[1])
    #     subprocess.call(res)

#####################################################
# test get context 
#####################################################

active_window = subprocess.check_output(['/usr/bin/xdotool','getactivewindow'])

active_window = active_window.strip().decode('UTF-8')

# print(active_window)



windowclass = subprocess.check_output(["xprop","-notype","-id",active_window,"WM_CLASS"])


windowclass = windowclass.strip().decode('UTF-8')
# print(windowclass)

expr= "WM_CLASS = \"([^\"]*)\", \"([^\"]*)\""
m = re.search(expr, windowclass)
print(m.group(2))
