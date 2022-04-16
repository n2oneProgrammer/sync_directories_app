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
            elements = normpath(line).split("\\")
            paths = normpath(name).split("\\")
            element_pointer = 0
            for path in paths:
                if path == elements[element_pointer]:
                    element_pointer += 1
                    if element_pointer >= len(elements):
                        return True
        return False

    def load_file(self):
        if os.path.exists(self.ignore_file_name):
            with open(self.ignore_file_name, "r") as file:
                data = file.readlines()
                for line in data:
                    self.ignore_file.append(line.strip())
