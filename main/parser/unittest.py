#
# Parser unit test
#
import pprint
import json


pp = pprint.PrettyPrinter(depth=4, width=5)


phrases = [
    "open nautilus", "open nautilus here", "open firefox", "close browser",
    "switch to firefox", "open max", "show firefox", "open terminal",
    "type alpha"
]

phrases = ["alpha","alpha charlie","alpha charlie three"]
# phrases = ["alpha"]

#
# Load rules file
#

rules_file = open("rules.json", "r")
rules = json.load(rules_file)
rules_file.close()
# Add a blank rule with the correct format

rule = {}
rule["NAME"] = "DEFAULT"
rule["SIGNATURE"] = "[VAR1][VAR2]"
rule["LENGTH"] = 2
rule["CONTEXT"] = "ALL"
rule["VARIABLES"] = {}
rule["VARIABLES"]["VARIABLE_LIST"] = ["VAR1", "VAR2"]
rule["VARIABLES"]["VAR1"] = {"opt1": "opt1"}
rule["VARIABLES"]["VAR2"] = {"opt1": "opt1"}

if rule["NAME"] not in rules:
    rules[rule["NAME"]] = rule

rules_file = open("rules.json", "w")
json.dump(rules, rules_file)
rules_file.close()

#####################################################
# Pre-compile rules
#####################################################

var_lookup = {}

for rule in rules:

    for var in rules[rule]["VARIABLES"]["VARIABLE_LIST"]:
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

                rule_graph[rule].append([var, word])


                graph[c][1].append(keyword)

                if keyword[0] not in rule_opt:
                    rule_opt[keyword[0]] = 0
                rule_opt[keyword[0]] += 1

    # for rule in rule_opt:
    #     rule_opt[rule] = rule_opt[rule] / phrase_lenght

    # pp.pprint(rule_graph)

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
                print("Matched")
                matches.append([rule,[subarr]])
            input("")

    print("\n")
    for match in matches:
        print(match)
