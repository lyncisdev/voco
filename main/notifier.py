import subprocess


class Notifier():
    def __init__(self):

        self.i3blocks_text_filename = "i3blocks_text.txt"
        self.color_dict = {
            'red': "#FF0000",
            'yellow': "#FFAE00",
            'white': "#FFFFFF"
        }

    def notify(self, message, color):
        '''
        write i3 blocks
        This function rights of the supporting file required by i3 blocks.
        I3 blocks is a GUI element of i3wm tiling window manager.
        '''

        i3blocks_text = open(self.i3blocks_text_filename, "w")
        i3blocks_text.write("%s\n\n%s\n" % (message, self.color_dict[color]))
        i3blocks_text.close()

        subprocess.Popen(["pkill", "-RTMIN+12", "i3blocks"])

    def clear(self):
        i3blocks_text = open(self.i3blocks_text_filename, "w")
        i3blocks_text.write("%s\n\n%s\n" % ("", self.color_dict["white"]))
        i3blocks_text.close()

        subprocess.Popen(["pkill", "-RTMIN+12", "i3blocks"])
