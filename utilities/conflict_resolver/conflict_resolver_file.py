from utilities.conflict import Conflict
from filecmp import dircmp
import difflib

START_DIFF = ">>>>>>>>>>>>>>>>"
END_DIFF = "<<<<<<<<<<<<<<<<"
BETWEEN_DIFF = "----------------"


class ConflictResolverFile:

    def __init__(self, conflict: Conflict, sync_core):
        self.conflict = conflict
        self.sync_core = sync_core

    def get_content_path1(self):
        with open(self.conflict.path1, "r") as file:
            # TODO(any): Check if file is binary

            content = file.readlines()
        return content

    def get_content_path2(self):
        with open(self.conflict.path2, "r") as file:
            # TODO(any): Check if file is binary

            content = file.readlines()
        return content

    def resolve(self, new_content):
        self.sync_core.resolve_conflict(self.conflict.path1, self.conflict.path2,
                                        new_content)

    def get_diff(self):
        is_new_conflict = ""
        last = ""
        result = ""

        for line in list(difflib.unified_diff(self.get_content_path1(), self.get_content_path2()))[2:] + [""]:
            if line.startswith("@@"):
                continue
            if line.startswith("-"):
                if is_new_conflict == "":
                    result += START_DIFF + " Left"

                    is_new_conflict = "-"
                elif is_new_conflict == "+" and last == "+":
                    result += BETWEEN_DIFF
                last = "-"
                result += line.strip()
            elif line.startswith("+"):
                if is_new_conflict == "":
                    result += START_DIFF + " Right"
                    is_new_conflict = "+"
                elif is_new_conflict == "-" and last == "-":
                    result += BETWEEN_DIFF
                last = "+"
                result += line.strip()
            else:
                if is_new_conflict == "-":
                    result += END_DIFF + " Right"
                elif is_new_conflict == "+":
                    result += END_DIFF + " Left"
                last = ""
                is_new_conflict = ""
                result += line.strip()
            result += "\n"
        return result[:-1]
