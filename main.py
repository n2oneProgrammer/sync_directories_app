import os

from PIL import Image
from pystray import Icon, Menu, MenuItem

from utilities.path import get_icon_path, get_name


class Tray:
    __instance = None

    @staticmethod
    def getInstance():
        if Tray.__instance == None:
            Tray()
        return Tray.__instance

    def __init__(self):

        if Tray.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Tray.__instance = self

        self.n = False
        self.icon = Icon(get_name(), title=get_name())
        self.icon.icon = Image.open(get_icon_path())
        self.icon.menu = Menu(
            MenuItem("run", self.start_app), MenuItem("close", self.exit)
        )

    def run(self):
        self.icon.run()

    def exit(self):
        os._exit(0)

    def start_app(self):
        from app import App

        App.getInstance().run()


if __name__ == "__main__":
    # from app import App

    # App.getInstance().run()
    t = Tray.getInstance()
    t.run()
