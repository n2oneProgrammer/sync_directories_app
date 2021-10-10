import os

from PIL import Image
from pystray import Icon, Menu, MenuItem

from utilities.folder import Folder
from utilities.notification import Notification
from utilities.path import get_icon_path, get_name


class Tray:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.__instance._init()
        return cls.__instance

    def _init(self):
        self.length_sync = -1
        self.icon = Icon(get_name(), title=get_name())
        self.icon.icon = Image.open(get_icon_path())
        self.icon.menu = Menu(
            MenuItem("Run", self.start_app),
            MenuItem("Sync now", self.sync_now),
            MenuItem("Close", self.exit),
        )

    def sync_now(self):
        list = Folder.load_all(callback=self.sync_now_callback)
        self.length_sync = len(list)
        Notification().notify("Sync", f"Syncs {len(list)} folders.")

    def sync_now_callback(self):
        if self.length_sync < 0:
            return
        self.length_sync = -1
        Notification().notify("Sync", f"Syncs complited!")

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
    # Tray().run()
