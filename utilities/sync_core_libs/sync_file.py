import os

from utilities.sync_core_libs.diff_type import DiffType


class SyncFile:
    def __init__(self, src1, src2, type, status):
        self.src1 = src1
        self.src2 = src2
        self.type = type
        self.status = status
        self.error = None

    def __str__(self):
        return f"{self.type}: {self.src1} - {self.src2} | {self.status}"

    def get_name(self):
        if self.type is DiffType.Create:
            return os.path.basename(self.src1)
        elif self.type is DiffType.Delete:
            return None
        elif self.type is DiffType.Edit:
            return f"{os.path.basename(self.src1)} -> {os.path.basename(self.src2)}"
        elif self.type is DiffType.RemoveRemove:
            return None
        return None

    def set_error(self, error):
        self.error = error
        self.type = DiffType.Error

    def get_conflict(self):
        if self.type in [
            DiffType.AddAddConflict,
            DiffType.EditEditConflict,
            DiffType.RemoveEditConflict,
            DiffType.Error,
        ]:
            return self
        return None
