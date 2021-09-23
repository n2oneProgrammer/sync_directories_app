import os
import sys

from appdirs import user_data_dir


def convert_path(path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS) + "\\" + path
    return path


def get_icon_path():
    return convert_path("assets/icon/icon.png")


def get_name():
    return "SyncDirectories"


def get_storage():
    dir = user_data_dir(get_name(), "jaanonim")
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir
