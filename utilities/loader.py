import os

from kivy.lang import Builder


def load_kv():
    dirs = ["pages/kv", "components/kv"]
    for d in dirs:
        load_dir(d)


def load_dir(dir):
    for kv_file in os.listdir(dir):
        with open(os.path.join(dir, kv_file), encoding="utf-8") as kv:
            try:
                Builder.load_string(kv.read())
            except Exception as e:
                raise Exception(f"IN FILE: {kv_file}", str(e))
