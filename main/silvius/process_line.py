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
    'keynav',
    'jump',  #jump within EMACS
    'dictate'
]

letters = [
    'alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf', 'hotel',
    'india', 'juliet', 'kilo', 'lima', 'mike', 'november', 'oscar', 'papa',
    'quebec', 'romeo', 'sierra', 'tango', 'uniform', 'victor', 'whiskey',
    'whisky', 'x-ray', 'yankee', 'zulu'
]

numbers = {
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'zero': 0
}


def c_rofi_switch(word_array):
    # open rofi in window switcher mode
    if len(word_array) > 1:
        if word_array[1] == "window":
            cmd = XDO_TOOL + 'key ctrl+alt+Tab'
        elif word_array[1] == "firefox":
            cmd = XDO_TOOL + 'search "Mozilla Firefox" windowactivate'
        elif word_array[1] == "terminal":
            cmd = XDO_TOOL + 'search --name "mainterm" windowactivate'
        elif word_array[1] == "term":
            cmd = XDO_TOOL + 'search --name "mainterm" windowactivate'
        elif word_array[1] == "max":
            cmd = XDO_TOOL + 'search --name "emacs." windowactivate'
        else:
            cmd = 'rofi -show window'
    elif len(word_array) == 1:
        cmd = 'rofi -show window'

    return cmd


def c_rofi_run(word_array):
    # open rofi in run mode
    cmd = 'rofi -show run'
    return cmd

# Keynav is not fully implemented yet
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


def c_jump_commands(word_array):

    # if numbers then jump to line
    # if letters jump to character
    is_letters = True
    is_numbers = True

    for word in word_array[1:]:
        if word not in letters:
            is_letters = False

    for word in word_array[1:]:
        if word not in numbers:
            is_numbers = False

    if (not is_numbers) and (not is_letters):
        # error
        cmd = ''
        return cmd

    else:

        if is_letters:
            if len(word_array[1:]) <= 1:
                line = ['space', 'juliet', 'juliet'] + word_array[1:]

            else:
                line = ['space', 'juliet', 'sky', 'juliet'] + word_array[1:3]

        else:
            line = word_array[1:] + ['sky', 'golf']

        line = ' '.join(line)

        tokens = scan(line)
        ast = parse(tokens)
        cmd = execute(ast, True)
        return cmd


def c_dictate_commands(word_array):
    # set a flag that the next audio clip should be processed by the ASPIRE CHAIN MODEL

    return "DICTATE_FLAG"


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
    'keynav': c_keynav,
    'jump': c_jump_commands,
    'dictate': c_dictate_commands
}


def check_escape_keywords(line):
    word_array = line.lower().split()
    if word_array[0] in escape_keywords:
        return True
    else:
        return False


def process_line(line):
    word_array = line.lower().split()

    # process locally of one of the escape keywords was used
    if word_array[0] in escape_keywords:
        try:
            level_0 = word_array[0]
            #            print(level_0)
            cmd = function_dict[level_0](word_array)
        except:
            cmd = ""

    # otherwise send to Silvius
    else:
        tokens = scan(line)

        try:
            ast = parse(tokens)
            # printAST(ast)
            cmd = execute(ast, True)
        except:
            cmd = ""
            print("")

    return cmd
