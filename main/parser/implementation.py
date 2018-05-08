




#
# Parser rules implementation
#


XDO_TOOL = '/usr/bin/xdotool '

def r_type_character(variables):

# "VARIABLE_LIST": ["CHARACTER"],

    char = variables["CHARACTER"][0]

    return XDO_TOOL + "key " + char


