#
# Parser unit test
#

import pprint
import json
import subprocess
import re

import parser

pp = pprint.PrettyPrinter(depth=4, width=5)


# Add a blank rule with the correct format
# rule = {}
# rule["NAME"] = "DEFAULT"
# rule["SIGNATURE"] = "[VAR1][VAR2]"
# rule["LENGTH"] = 2
# rule["CONTEXT"] = "ALL"
# rule["VARIABLES"] = {}
# rule["VARIABLES"]["VAR1"] = {"opt1": "opt1"}
# rule["VARIABLES"]["VAR2"] = {"opt1": "opt1"}

#####################################################
# test rules on phrases 
#####################################################


phrases = [
    "open nautilus", "open nautilus here", "open firefox", "close browser",
    "switch to firefox", "open max", "show firefox", "open terminal",
    "type alpha"
]

phrases = ["alpha","alpha charlie","alpha charlie three firefox","alpha charlie three open firefox"]


phrases = ["new shift alpha"]


dynamic_rules,static_rules, var_lookup = parser.init()

for phrase in phrases:
    print("\n------------------------\n%s\n------------------------" % phrase)


    commands,matches = parser.parsephrase(dynamic_rules,static_rules,var_lookup,phrase,"")
    print("\n\n\n")
    pp.pprint(commands)
