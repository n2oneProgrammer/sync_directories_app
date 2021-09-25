from utilities.folder import Conflict, Folder


class ConflictResolverAddAdd:

    def __init__(self, conflict: Conflict, folder: Folder):
        self.conflict = conflict

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
        print("asdf")
