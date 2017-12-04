
'''
Python interpreter

This is a demonstration function to improve on EMACS' jump


'''


import pprint
import re

text = """while (True):
    data = stream.read(chunk)
    rms = audioop.rms(data, 2)

    if debug:
        print(rms)

    if rec == False:
        if rms >= gate:
            audio_sample = []
            audio_sample.append(prev_sample)
            audio_sample.append(data)
            rec = True
            timeout = 0
"""

s = text.split("\n")

line = s[10]



element_array = []
last_index = 0
flag = 'A'

# for element in re.split("[:,\s,(,)]\s*",line):
for element in re.split("(\W)",line):
    length = len(element)
    if length > 0:
        begin = line.index(element, last_index)
        element_array.append([flag, begin, length, element])
        last_index = begin
        if element != " ":
            flag = chr(ord(flag) + 1)

flag_string = ""

for element in element_array:
    length = element[2]
    breakpoint = int(length/2)
    for x in range(0, length):
        if x < breakpoint:
            if x == 0:
                flag_string += "|"
            else:
                flag_string += " "
        elif x == breakpoint:
            if element[3] != " ":
                flag_string += element[0]
            else:
                flag_string += " "
        else:
            if x == length-1:
                flag_string += "|"
            else:
                flag_string += " "


# pp = pprint.PrettyPrinter(depth=3, width=5)
# pp.pprint(element_array)

print(flag_string)

print(line)

