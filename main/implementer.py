import pyautogui


class Implementer():
    def execute(self, cmd):
        if cmd is not None:
            if len(cmd) > 1:
                pyautogui.typewrite(cmd, interval=0.01)
