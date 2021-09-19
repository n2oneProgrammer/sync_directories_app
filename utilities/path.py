import os
import sys


def convert_path(path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS) + "\\" + path
    return path

def get_icon_path():
    return convert_path('icon.ico')
