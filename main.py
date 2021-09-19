import time
from threading import Thread

from PIL import Image
from pystray import Icon, Menu, MenuItem

from utilities.path import get_icon_path


class Tray:
    def __init__(self):
        self.initialzed = False
        self.icon = Icon("SyncDirectories", title="SyncDirectories")
        self.icon.icon = Image.open(get_icon_path())
        self.icon.menu = Menu(MenuItem("run", self.start_app))
        self.icon.run()

    def notify(self, title, message, duration=3):
        Thread(
            target=self._notify,
            name="Notifcation",
            args=(
                title,
                message,
                duration,
            ),
        ).start()

    def _notify(self, title, message, duration):
        self.icon.notify(title=title, message=message)
        time.sleep(duration)
        self.icon.remove_notification()

    def start_app(self):
        from app import init, run

        if not self.initialzed:
            init()
        run()


if __name__ == "__main__":
    Tray()
