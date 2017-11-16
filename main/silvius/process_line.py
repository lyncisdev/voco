from scan import scan
from parse import parse
from execute import execute
from errors import GrammaticalError
from ast import printAST
import pdb
import os

# the escape keywords are intended for short commands, which start with the escape keyword, that have a vey specific objective and a 1-to-1 mapping between command and action

XDO_TOOL = '/usr/bin/xdotool '

escape_keywords = [
    'switch',
    'run',
    'window',  # for tiling and moving windows
    'goto',  # for moving the cursor - need to train voice on one-word goto
    'snippet',  # for inserting a code snippet
    'copy',  # copy
    'paste',  # paste
    'select',  # for selecting lines or words
    'emacs',  # Emacs command to follow
    'keynav'
]

silvius_keywords = [
    'control', 'alt', 'super', 'shift', 'comma', 'act', 'ampersand', 'alpha',
    'backslash', 'bang', 'bravo', 'carrot', 'charlie', 'colon', 'delta',
    'dollar', 'dot', 'down', 'escape', 'echo', 'enter', 'eco', 'eight',
    'equal', 'expert', 'five', 'four', 'foxtrot', 'golf', 'hash', 'hotel',
    'india', 'juliet', 'kilo', 'late', 'left', 'lima', 'mike', 'minus', 'nine',
    'november', 'one', 'oscar', 'papa', 'percent', 'plus', 'phrase', 'quebec',
    'question', 'rate', 'right', 'romeo', 'scratch', 'sentence', 'seven',
    'sierra', 'six', 'sky', 'slap', 'slash', 'space', 'star', 'backspace',
    'tab', 'tango', 'three', 'two', 'underscore', 'uniform', 'up', 'victor',
    'whiskey', 'whisky', 'word', 'x-ray', 'yankee', 'zero', 'zulu'
]


def c_rofi_switch(word_array):
    # open rofi in window switcher mode
    if len(word_array) > 1:
        if word_array[1] == "window":
            cmd = XDO_TOOL + 'key ctrl+alt+Tab'
        elif word_array[1] == "firefox":
            cmd = XDO_TOOL + 'search "Mozilla Firefox" windowactivate'
        elif word_array[1] == "terminal":
            cmd = XDO_TOOL + 'search "Terminal" windowactivate'
        elif word_array[1] == "max":
            cmd = XDO_TOOL + 'search "Emacs" windowactivate'
        else:
            cmd = 'rofi -show window'
    elif len(word_array) == 1:
        cmd = 'rofi -show window'

    return cmd


def c_rofi_run(word_array):
    # open rofi in run mode
    cmd = 'rofi -show run'
    return cmd

def c_keynav(word_array):
    '''
    h : select the left half of the region
    j : select the bottom half of the region
    k : select the top half of the region
    l : select the right half of the region
    shift+h : move the region left
    shift+j : move the region down
    shift+k : move the region top
    shift+l : move the region right
    semicolon : Move the mouse to the center of the selected region
    spacebar : Move the mouse and left-click
    escape : Cancel the move
    '''
    if len(word_array) > 1:
        if word_array[1] == "golf":
            cmd = 'keynav grid-nav'
        else:
            cmd = 'keynav'
    else:
        cmd = 'keynav'

    return cmd

def c_window_commands(word_array):

    # window commands
    # returns string command for xdo tool

    sub_cmd = {
        'tile': 'shortcut_undefined',
        'center': 'key ctrl+alt+5',
        'left': 'key ctrl+alt+4',
        'right': 'key ctrl+alt+6',
        'top': 'key ctrl+alt+8',
        'bottom': 'key ctrl+alt+2'
    }

    # Look up command in the dictionary, catch error if its not found
    try:
        cmd = XDO_TOOL + sub_cmd[word_array[1]]
    except:
        cmd = ""

    return cmd


def c_goto_commands(word_array):
    # window commands
    # returns string command for xdo tool
    cmd = "c_goto_commands"
    print(cmd)
    return cmd


def c_snippet_commands(word_array):
    # window commands
    # returns string command for xdo tool
    cmd = "c_snippet_commands"
    print(cmd)
    return cmd


def c_select_commands(word_array):
    # window commands
    # returns string command for xdo tool
    cmd = "c_select_commands"
    print(cmd)
    return cmd


def c_emacs_commands(word_array):
    # window commands
    # returns string command for xdo tool
    cmd = "c_emacs_commands"
    print(cmd)
    return cmd


def c_copypaste_commands(word_array):
    # window commands
    # returns string command for xdo tool

    #    print(word_array)
    if word_array[0] == 'copy':
        if len(word_array) == 2:
            if word_array[1] == 'term':
                cmd = XDO_TOOL + "key ctrl+shift+c"
        else:
            cmd = XDO_TOOL + "key ctrl+c"
    elif word_array[0] == 'paste':
        if len(word_array) == 2:
            if word_array[1] == 'term':
                cmd = XDO_TOOL + "key ctrl+shift+v"
        else:
            cmd = XDO_TOOL + "key ctrl+v"
    else:
        cmd = ''

    return cmd


function_dict = {
    'switch': c_rofi_switch,
    'run': c_rofi_run,
    'window': c_window_commands,
    'goto': c_goto_commands,
    'snippet': c_snippet_commands,
    'select': c_select_commands,
    'max': c_emacs_commands,
    'copy': c_copypaste_commands,
    'paste': c_copypaste_commands,
    'keynav': c_keynav
}


def check_escape_keywords(line):
    word_array = line.lower().split()
    if word_array[0] in escape_keywords:
        return True
    else:
        return False


def process_line(line):
    word_array = line.lower().split()

    if word_array[0] in escape_keywords:
        try:
            level_0 = word_array[0]
            #            print(level_0)
            cmd = function_dict[level_0](word_array)
        except:
            cmd = ""

    elif word_array[0] in silvius_keywords:
        tokens = scan(line)
        ast = parse(tokens)
        #printAST(ast)
        cmd = execute(ast, True)
    else:
        cmd = ""

    return cmd
