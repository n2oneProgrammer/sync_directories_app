import os
import re
import string
import sys
import unicodedata

from appdirs import user_data_dir

VALID_CHARS = "-_.() %s%s" % (string.ascii_letters, string.digits)
RESERVED = [
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
    ".",
    "..",
    "",
    " ",
]


def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = "".join(c for c in value if c in VALID_CHARS)
    if value in RESERVED:
        value = ".file"
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def convert_path(path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS) + "\\" + path
    return path


def get_self_path():
    if getattr(sys, "frozen", False):
        return sys.executable
    else:
        return None


def get_icon_path():
    return convert_path("assets/icon/icon.png")


def get_name():
    return "SyncDirectories"


def get_package_name():
    return "com.jaanonim.syncdirectories"


def get_storage():
    dir = user_data_dir(get_name(), "jaanonim")
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir
