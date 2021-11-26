import os

from PIL import Image
from pystray import Icon, Menu, MenuItem

from utilities.autostart import Autostart
from utilities.device_listener import DeviceListener
from utilities.notification import Notification
from utilities.path import get_icon_path, get_name
from utilities.storage import Storage


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
            MenuItem("Open", self.start_app),
            MenuItem("Sync now", self.sync_now),
            MenuItem("Close", self.exit),
        )
        Autostart().update()

    def sync_now(self):
        Storage().sync_all()
        Notification().notify("Sync", f"Syncs {len(Storage().syncs)} folders.")

    def run(self):
        DeviceListener(self.sync_now).start()
        self.icon.run()

    def exit(self):
        os._exit(0)

    def start_app(self):
        from app import App

        App().run()


if __name__ == "__main__":
    Tray().run()
