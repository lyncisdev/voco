




#
# Parser rules implementation
#


XDO_TOOL = '/usr/bin/xdotool'

def r_type_character(variables):


    # "SIGNATURE": ["CHARACTER"],
    char = variables["CHARACTER"][1]

    return [XDO_TOOL,"key",char]

def r_type_number(variables):


    # "SIGNATURE": ["CHARACTER"],
    num = variables["NUMBER"][1]

    return [XDO_TOOL,"key",num]



def r_type_uppercase_character(variables):


    # "SIGNATURE": ["CHARACTER"],
    char = variables["CHARACTER"][1].upper()

    return [XDO_TOOL,"key",char]


def r_test():
    print("Test")
