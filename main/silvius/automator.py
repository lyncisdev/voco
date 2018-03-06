import os


class Automator:
    def __init__(self, real=True):
        self.xdo_list = []
        self.real = real

    def xdo(self, xdo):
        self.xdo_list.append(xdo)

    def xdo_pre(self,xdo):
        self.xdo_list.insert(0,xdo)

    def flush(self):
        if len(self.xdo_list) == 0: return

        command = '/usr/bin/xdotool'
        command += ''.join(self.xdo_list)
        #        self.execute(command)
        self.xdo_list = []
        return command

    def execute(self, command):
        if command == '': return
        # if self.real:
            # os.system(command)

    def raw_key(self, k):
        if (k == "'"): k = 'apostrophe'
        elif (k == '.'): k = 'period'
        elif (k == '-'): k = 'minus'
        self.xdo(' key ' + k)

    def key(self, k):
        # print(type(k))
        if (len(k) > 1): k = k.capitalize()
        self.xdo(' key ' + k)

    def type_word(self, k):

        for l in k:
            if l == ' ':
                self.xdo(' key Space')
            else:
                self.xdo(' key ' + l)


    def modifier(self, k):
        self.xdo_pre(' key ' + str(k))

    def modified(self, k):
        self.xdo('+' + str(k))
