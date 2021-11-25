import os
import re
import sys
import unicodedata

from appdirs import user_data_dir


def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def convert_path(path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS) + "\\" + path
    return path

def get_self_path():
    if getattr(sys, "frozen", False):
        return sys.executable
    else:
        return os.path.abspath(__file__)

def get_icon_path():
    return convert_path("assets/icon/icon.png")


def get_name():
    return "SyncDirectories"


def get_storage():
    dir = user_data_dir(get_name(), "jaanonim")
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir
