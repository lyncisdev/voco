from scan import scan
from ast import AST
from parse import parse
from execute import execute
from errors import GrammaticalError
from ast import printAST
import pdb
import os


#line = "alpha bravo sky November five"
line = "control five sky mike"
tokens = scan(line)

#print(tokens)

ast = parse(tokens)
#printAST(ast)

# make this return the XDO command

cmd = execute(ast, True)

print(cmd) 
r
