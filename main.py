import os

from PIL import Image
from pystray import Icon, Menu, MenuItem

from utilities.path import get_icon_path, get_name


class Tray:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.__instance._init()
        return cls.__instance

    def _init(self):
        self.n = False
        self.icon = Icon(get_name(), title=get_name())
        self.icon.icon = Image.open(get_icon_path())
        self.icon.menu = Menu(
            MenuItem("Run", self.start_app), MenuItem("Close", self.exit)
        )

    def run(self):
        self.icon.run()

    def exit(self):
        os._exit(0)

    def start_app(self):
        from app import App

        App().run()


if __name__ == "__main__":

    # TODO: Remove debug
    from app import App

    App().run()
    # Tray.getInstance().run()
