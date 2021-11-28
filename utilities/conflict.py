from os.path import normpath

from utilities.sync_core_libs.diff_type import DiffType


class Conflict:
    def __init__(self, path1, path2, type: DiffType):
        self.path1 = normpath(path1)
        self.path2 = normpath(path2)
        self.type = type
        self.error = None

    def set_error(self, error):
        self.error = error
        self.type = DiffType.Error

    def __str__(self):
        return f"{self.type}: {self.path1} - {self.path2}"
