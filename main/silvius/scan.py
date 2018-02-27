import re

# these are the generic silvius grammar keywords

keywords = [
    'control', 'alt', 'super', 'shift', 'comma', 'act', 'ampersand', 'alpha',
    'backslash', 'bang', 'bravo', 'carrot', 'charlie', 'colon', 'delta',
    'dollar', 'dot', 'down', 'escape', 'echo', 'enter', 'eco', 'eight',
    'equal', 'expert', 'five', 'four', 'foxtrot', 'golf', 'hash', 'hotel',
    'india', 'juliet', 'kilo', 'late', 'left', 'lima', 'mike', 'minus', 'nine',
    'november', 'one', 'oscar', 'papa', 'percent', 'plus', 'phrase', 'quebec',
    'question', 'rate', 'right', 'romeo', 'scratch', 'sentence', 'seven',
    'sierra', 'six', 'sky', 'slap', 'slash', 'space', 'star', 'backspace',
    'tab', 'tango', 'three', 'two', 'underscore', 'uniform', 'up', 'victor',
    'whiskey', 'whisky', 'word', 'x-ray', 'yankee', 'zero', 'zulu', 'home', 'end', 'pageup', 'pagedown', 'singlequote', 'doublequote', 'delete', 'mod', 'las','bas'
]


class Token:
    def __init__(self, type, wordno=-1, extra=''):
        self.type = type
        self.extra = extra
        self.wordno = wordno

    def __cmp__(self, o):
        return cmp(self.type, o)

    def __repr__(self):
        return str(self.type)


def scan(line):
    tokens = []
    wordno = 0

    for t in line.lower().split():
        wordno += 1
        if (t in keywords):
            tokens.append(Token(t, wordno))
        else:
            tokens.append(Token('ANY', wordno, t))

    tokens.append(Token('END'))

    return tokens
