from scan import scan
from ast import AST
from parse import parse
from execute import execute
from errors import GrammaticalError
from ast import printAST
from process_line import process_line
import pdb
import os


# line = "alpha bravo sky November five"

# line = "charlie slap down two"

# print(process_line(line))


# line = "slap six"

# print(process_line(line))


line = "jump six zero seven"
print(process_line(line))


line = "jump alpha bravo charlie"
print(process_line(line))

line = "jump alpha "
print(process_line(line))

line = "jump"
print(process_line(line))


line = "jump one oscar"
print(process_line(line))


line = "dictate"
print(process_line(line))




#tokens = scan(line)

#print(tokens)

#ast = parse(tokens)
#printAST(ast)

# make this return the XDO command

#cmd = execute(ast, True)

# print(cmd) 
