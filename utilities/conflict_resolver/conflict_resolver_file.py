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

    def is_resolved(self, new_content: str):
        found_line = -1
        if found_line == -1:
            found_line = new_content.find(START_DIFF)
        if found_line == -1:
            found_line = new_content.find(END_DIFF)
        if found_line == -1:
            found_line = new_content.find(BETWEEN_DIFF)
        return found_line

    def get_diff(self):
        is_new_conflict = ""
        last = ""
        result = ""

        for line in list(difflib.unified_diff(self.get_content_path1(), self.get_content_path2()))[2:] + [""]:
            if line.startswith("@@"):
                continue
            if line.startswith("-"):
                if is_new_conflict == "":
                    result += START_DIFF + " Left\n"

                    is_new_conflict = "-"
                elif is_new_conflict == "+" and last == "+":
                    result += BETWEEN_DIFF + "\n"
                last = "-"
                result += line.strip() + "\n"
            elif line.startswith("+"):
                if is_new_conflict == "":
                    result += START_DIFF + " Right\n"
                    is_new_conflict = "+"
                elif is_new_conflict == "-" and last == "-":
                    result += BETWEEN_DIFF + "\n"
                last = "+"
                result += line.strip() + "\n"
            else:
                if is_new_conflict == "-":
                    result += END_DIFF + " Right\n"
                elif is_new_conflict == "+":
                    result += END_DIFF + " Left\n"
                last = ""
                is_new_conflict = ""
                result += line.strip() + "\n"
        return result
