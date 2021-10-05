from utilities.folder import Conflict, Folder


class ConflictResolverFile:

    def __init__(self, conflict: Conflict, sync_core):
        self.conflict = conflict
        self.sync_core = sync_core

    def get_content_path1(self):
        with open(self.conflict.path1, "r") as file:
            # TODO(any): Check if file is binary

            content = file.read()
        return content

    def get_content_path2(self):
        with open(self.conflict.path2, "r") as file:
            # TODO(any): Check if file is binary

            content = file.read()
        return content

    def resolve(self, new_content):
        self.sync_core.resolve_conflict(self.conflict.path1, self.conflict.path2,
        new_content)
