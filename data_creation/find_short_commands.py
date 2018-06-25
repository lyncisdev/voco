
text_file = open("VoxForgeDict", 'r')

text_lines = text_file.readlines()


# suod            [SUDO]          s uw d ow
# forloop         [FORLOOP]       f ao r l uw p
# doublequote     [DOUBLEQUOTE]   d ah b ah l k w ow t
# pagedown        [PAGEDOWN]      p ey jh d aw n

for line in text_lines:

    parts = line.split("[")
    parts = parts[1].split("]")[0]
    if len(parts) <= 3 and len(parts) >= 2:

        print(parts)

