#
# Parser.py
#

import pprint
import json
import subprocess
from .implementation import *
import re
import pprint



pp = pprint.PrettyPrinter(depth=4, width=5)

basedir = "parser/"

def init():

    #####################################################
    # load rules files
    #####################################################

    rules_file = open(basedir + "rules.json", "r")
    rules = json.load(rules_file)
    rules_file.close()



    variables_file = open(basedir + "variables.json", "r")
    variables = json.load(variables_file)
    variables_file.close()

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

    rules_lookup_file = open(basedir + "rules_lookup.json", "w")
    json.dump(var_lookup, rules_lookup_file)

    return rules, var_lookup

def parsephrase(rules, var_lookup,phrase):



    # pp.pprint(globals())
    # pp.pprint(locals())


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

    # print("\nCandidate rules")
    # for match in matches:
    #     print(match)


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

    # print("\nFinal set")
    # for match in final_match:
    #     print(match)

    # sort by index

    final_match.sort(key=lambda elem: elem[1][0][2])


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

    print("\n\n\n")
    for match in final_match:
        print(match)

    print("\n\n\n")
    # # execute command

    cmd = []

    for match in final_match:


        function_name = rules[match[0]]["FUNCTION"]
        # print(function_name)
        # tmp = function_name(match[1])
        cmd.append(globals()[function_name](match[1]))

        # pp.pprint(globals())
        # t = r_test() 
    return cmd
