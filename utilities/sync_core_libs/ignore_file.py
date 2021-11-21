import os

from utilities.settings import Settings


class IgnoreFile:

    def __init__(self, src_dir):
        self.ignore_file_name = Settings().get("Ignore_file_name")
        if self.ignore_file_name is None:
            self.ignore_file_name = ".ignore_sync"
        self.ignore_file_name = os.path.join(src_dir, self.ignore_file_name)
        self.ignore_file = []
        self.load_file()

    def is_detect(self, name):
        for line in self.ignore_file:
            if name == line:
                return True
        return False

    def load_file(self):
        with open(self.ignore_file_name, "r") as file:
            data = file.readlines()
            for line in data:
                self.ignore_file.append(line)
