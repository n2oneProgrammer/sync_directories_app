import os
import sys

from kivy.lang import Builder
from kivy.resources import resource_add_path


def load_kv():
    dirs = ["pages\kv", "components\kv"]

    for d in dirs:
        if hasattr(sys, "_MEIPASS"):
            load_dir(os.path.join(sys._MEIPASS) + "\\" + d)


def load_dir(dir):
    for kv_file in os.listdir(dir):
        with open(os.path.join(dir, kv_file), encoding="utf-8") as kv:
            try:
                Builder.load_string(kv.read())
            except Exception as e:
                raise Exception(f"IN FILE: {kv_file}", str(e))
