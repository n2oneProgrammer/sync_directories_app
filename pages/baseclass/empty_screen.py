from kivy.uix.screenmanager import Screen
from utilities.screens import ScreensUtilities


class EmptyScreen(Screen):
    def on_enter(self, *args):
        super().on_enter(*args)
        ScreensUtilities().start()
