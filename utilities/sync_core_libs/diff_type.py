from enum import Enum


class DiffType(Enum):
    AddAddConflict = "file-plus"
    RemoveEditConflict = "file-remove"
    EditEditConflict = "file-edit"
    Create = "create"
    Edit = "edit"
    Delete = "delete"
    RemoveRemove = "removeremove"
    Same = "same"
