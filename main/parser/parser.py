#
# Parser.py
#

import pprint
import json
import subprocess
import re
import pprint

from .implementation import *
# from implementation import *

pp = pprint.PrettyPrinter(depth=4, width=5)

basedir = "parser/"

# basedir = ""


def init():

    #####################################################
    # load dynamic_rules files
    #####################################################

    dynamic_rules_file = open(basedir + "dynamic_rules.json", "r")
    dynamic_rules = json.load(dynamic_rules_file)
    dynamic_rules_file.close()

    static_rules_file = open(basedir + "static_rules.json", "r")
    static_rules = json.load(static_rules_file)
    static_rules_file.close()

    variables_file = open(basedir + "variables.json", "r")
    variables = json.load(variables_file)
    variables_file.close()

    #####################################################
    # insert repeated variables
    #####################################################

    for var in variables:
        val = variables[var]
        if isinstance(val, list):
            tmp_dict = {}
            for elem in val:
                tmp_dict.update(variables[elem])
            variables[var] = tmp_dict

    for rule in dynamic_rules:
        for var in dynamic_rules[rule]["VARIABLES"]:

            val = dynamic_rules[rule]["VARIABLES"][var]
            if not isinstance(val, dict):
                if val in variables:
                    dynamic_rules[rule]["VARIABLES"][var] = variables[val]
                # else:
                # print("error")

                #####################################################
                # Pre-compile dynamic_rules
                #####################################################

    var_lookup = {}

    for rule in dynamic_rules:

        for var in dynamic_rules[rule]["SIGNATURE"]:
            for word in dynamic_rules[rule]["VARIABLES"][var]:
                if word not in var_lookup:
                    var_lookup[word] = []

                var_lookup[word].append([rule, var])

    dynamic_rules_lookup_file = open(basedir + "dynamic_rules_lookup.json",
                                     "w")
    json.dump(var_lookup, dynamic_rules_lookup_file)

    json.dump(variables, open(basedir + "variables_final.json", "w"))
    json.dump(dynamic_rules, open(basedir + "dynamic_rules_final.json", "w"))

    return dynamic_rules, static_rules, var_lookup


def parsephrase(dynamic_rules,
                static_rules,
                var_lookup,
                phrase,
                context,
                ignore_context=False):

    words = phrase.split()
    phrase_lenght = len(words)

    ############################################
    # match static rules
    ############################################

    # pp.pprint(static_rules)

    matches = []
    for rule in static_rules:
        if ("ALL" in static_rules[rule]["CONTEXT"]) or (
                context in static_rules[rule]["CONTEXT"]) or (ignore_context):

            for elem in static_rules[rule]["RULES"]:

                sig = elem.split(" ")
                # print(sig)
                l = len(sig)
                for x in range(0, len(words) - l + 1):
                    subarr = words[x:x + l]

                    match = True
                    for y in range(0, l):
                        if sig[y] != subarr[y]:
                            match = False
                    if match == True:

                        tmp = []
                        for y in range(0, l):
                            tmp.append([
                                sig[y], sig[y], x + y,
                                static_rules[rule]["RULES"][elem]
                            ])

                        matches.append([rule, tmp])

    # print("match")
    # print(matches)
    # print(phrase)
    # print(words)
    ############################################
    # match dynamic rules
    ############################################

    rule_graph = {}

    for c, word in enumerate(words):
        if word in var_lookup:
            for elem in var_lookup[word]:
                rule = elem[0]
                var = elem[1]
                lookup_val = dynamic_rules[rule]["VARIABLES"][var][word]
                if rule not in rule_graph:
                    rule_graph[rule] = []
                if [var, word, c, lookup_val] not in rule_graph[rule]:
                    rule_graph[rule].append([var, word, c, lookup_val])

    new_rule_graph = {}
    # Remove dynamic_rules that don't match context

    for rule in rule_graph:
        if ("ALL" in dynamic_rules[rule]["CONTEXT"] ) or (
                context in dynamic_rules[rule]["CONTEXT"]) or (ignore_context):
            new_rule_graph[rule] = rule_graph[rule]

    rule_graph = new_rule_graph

    # Remove dynamic_rules that don't fit

    new_rule_graph = {}

    for rule in rule_graph:
        if len(rule_graph[rule]) >= len(dynamic_rules[rule]["SIGNATURE"]):
            new_rule_graph[rule] = rule_graph[rule]

    rule_graph = new_rule_graph

    # pp.pprint(rule_graph)

    #########################################################

    for rule in rule_graph:

        # match dynamic_rules by comparing signatures

        l = len(dynamic_rules[rule]["SIGNATURE"])

        for x in range(0, len(rule_graph[rule]) - l + 1):
            match = True

            sig = dynamic_rules[rule]["SIGNATURE"]
            subarr = rule_graph[rule][x:x + l]

            for y in range(0, l):
                if sig[y] != subarr[y][0]:
                    match = False
            if match == True:
                matches.append([rule, subarr])

    # print("\nCandidate dynamic_rules")

    # pp.pprint(matches)
    # for match in matches:
    # print(match)

    # Build set representation
    match_set = {}
    for x, match in enumerate(matches):
        tmp = set()
        for elem in match[1]:
            tmp.add(elem[2])

        match_set[x] = tmp

    # try set cover solution
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

        # remove overlaps
        new_match_set = {}
        for x in match_set:
            if len(set.intersection(match_set[pos], match_set[x])) == 0:
                new_match_set[x] = match_set[x]
        match_set = new_match_set

    # print("\nFinal set")
    # for match in final_match:
    #     print(match)

    # sort by index

    final_match.sort(key=lambda elem: elem[1][0][2])

    # print("\nSorted Final set")
    # for match in final_match:
    #     print(match)

    coverage = set()

    for match in final_match:
        for elem in match[1]:
            coverage.add(elem[2])

    if len(coverage) == len(words):

        variables = []

        for match in final_match:
            tmp_arr = []
            for elem in match[1]:
                lookupval = elem[3]
                tmp_arr.append(lookupval)
            variables.append([match[0], tmp_arr])

        # print("\nPassed to function")
        # for match in final_match:
        #     print(match)

        cmd = []

        for match in variables:
            function_name = "r_" + match[0].lower()
            cmd.append(globals()[function_name](match[1], context))

        return cmd, final_match

    else:
        # print("Incomplete cover")
        return [], []
