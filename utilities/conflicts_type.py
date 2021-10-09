from enum import Enum


class ConflictsType(Enum):
    AddAdd = "file-plus"
    RemoveEdit = "file-remove"
    EditEdit = "file-edit"
