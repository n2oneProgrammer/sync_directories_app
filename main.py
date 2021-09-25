# import time
# from threading import Thread
#
# from PIL import Image
# from pystray import Icon, Menu, MenuItem
#
# from utilities.path import get_icon_path, get_name
#
#
# class Tray:
#     def __init__(self):
#         self.icon = Icon(get_name(), title=get_name())
#         self.icon.icon = Image.open(get_icon_path())
#         self.icon.menu = Menu(MenuItem("run", self.start_app))
#         self.icon.run()
#
#     def notify(self, title, message, duration=3):
#         Thread(
#             target=self._notify,
#             name="Notifcation",
#             args=(
#                 title,
#                 message,
#                 duration,
#             ),
#         ).start()
#
#     def _notify(self, title, message, duration):
#         self.icon.notify(title=title, message=message)
#         time.sleep(duration)
#         self.icon.remove_notification()
#
#     def start_app(self):
#         from app import App
#
#         App.getInstance().run()
#
#
# if __name__ == "__main__":
#     Tray()
import sys
from utilities.folder import Folder
from utilities.sync_core import SyncCore

if __name__ == "__main__":
    dirs = sys.argv[1:3]
    data = {}
    data["name"] = "test"
    data["dir1"] = dirs[0]
    data["dir2"] = dirs[1]
    dir = Folder(data)

