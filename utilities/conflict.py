from os.path import normpath

from utilities.conflicts_type import ConflictsType


class Conflict:
    def __init__(self, path1, path2, type: ConflictsType):
        self.path1 = normpath(path1)
        self.path2 = normpath(path2)
        self.type = type

    def resolve(self):
        pass
