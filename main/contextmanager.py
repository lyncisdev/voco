import subprocess
import re


class ContextManager():
    def getcontext(self):
        '''
            Get window context
            this function gets the class of window that is currently selected,
            for example Firefox or Emacs
            '''
        try:
            active_window = subprocess.check_output(
                ['/usr/bin/xdotool', 'getactivewindow'])

            active_window = active_window.strip().decode('UTF-8')

            windowclass = subprocess.check_output(
                ["xprop", "-notype", "-id", active_window, "WM_CLASS"])

            windowclass = windowclass.strip().decode('UTF-8')

            expr = "WM_CLASS = \"([^\"]*)\", \"([^\"]*)\""

            m = re.search(expr, windowclass)

            context = m.group(2).upper()

        except:
            context = ""

        return context
