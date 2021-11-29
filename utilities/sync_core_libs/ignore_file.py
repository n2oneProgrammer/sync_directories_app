import os
from os.path import normpath

from utilities.settings import Settings


class IgnoreFile:

    def __init__(self, src_dir):
        self.ignore_file_name = Settings().get("ignore_file_name")
        self.ignore_file = [self.ignore_file_name]
        self.ignore_file_name = os.path.join(src_dir, self.ignore_file_name)
        self.load_file()

    def is_detect(self, name):
        for line in self.ignore_file:
            if normpath(name) == normpath(line):
                return True
        return False

    def load_file(self):
        if os.path.exists(self.ignore_file_name):
            with open(self.ignore_file_name, "r") as file:
                data = file.readlines()
                for line in data:
                    self.ignore_file.append(line.strip())
