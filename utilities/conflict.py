from os.path import normpath

from utilities.sync_core_libs.diff_type import DiffType


class Conflict:
    def __init__(self, path1, path2, type: DiffType):
        self.path1 = normpath(path1)
        self.path2 = normpath(path2)
        self.type = type
