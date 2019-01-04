import keyboard


class InputManager():
    def register(self):
        def callback():
            print("Callback")

        keyboard.add_hotkey('ctrl+shift+a', callback)
