from enum import Enum


class ConflictsType(Enum):
    AddAdd = 0
    RemoveEdit = 1
    EditEdit = 2
