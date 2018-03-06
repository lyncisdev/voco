from scan import scan
from ast import AST
from parse import parse
from execute import execute
from errors import GrammaticalError
from ast import printAST
from process_line import process_line
import os


test_commands = [
    "python sudo top for in",
    "charlie slap down two",
    "mod alpha",
    "mod up",
    "mod shift alpha",
    "slap six",
    "alpha bravo sky November five",
    "equal zero seven",
    "space",
    "jump six zero seven",
    "jump alpha bravo charlie",
    "jump alpha ",
    "jump",
    "jump one oscar", #no functionality for mixed commands 
    "dictate"
]


for line in test_commands[0:1]:
    # print("\n%s\n%s" % (line, process_line(line,"LITERALMODE")))

    tokens = scan(line)
    ast = parse(tokens)
    printAST(ast)

    print("\n%s\n%s" % (line, process_line(line)))

