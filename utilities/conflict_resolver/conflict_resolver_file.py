import difflib

from utilities.conflict_resolver.content import Content
from utilities.sync_core_libs.sync_core import SyncFile

START_DIFF = ">>>>>>>>>>>>>>>>"
END_DIFF = "<<<<<<<<<<<<<<<<"
BETWEEN_DIFF = "----------------"


class ConflictResolverFile:
    def __init__(self, conflict, sync_core):
        self.conflict = conflict
        self.sync_core = sync_core

    def get_content_path1(self):
        try:
            with open(self.conflict.path1, "r") as file:
                text = file.readlines()
        except FileNotFoundError:
            return Content("", True, False, self.conflict.path1)
        except UnicodeDecodeError:
            return Content("", False, True, self.conflict.path1)
        return Content(text, False, False)

    def get_content_path2(self):
        try:
            with open(self.conflict.path2, "r") as file:
                text = file.readlines()
        except FileNotFoundError:
            return Content("", True, False, self.conflict.path2)
        except UnicodeDecodeError:
            return Content("", False, True, self.conflict.path2)
        return Content(text, False, False)

    def resolve(self, new_content):
        self.sync_core.resolve_conflict(
            SyncFile(
                self.conflict.path1, self.conflict.path2, self.conflict.type, None
            ),
            new_content,
        )

    def is_resolved(self, new_content: Content):
        found_line = -1
        if found_line == -1:
            found_line = new_content.text.find(START_DIFF)
        if found_line == -1:
            found_line = new_content.text.find(END_DIFF)
        if found_line == -1:
            found_line = new_content.text.find(BETWEEN_DIFF)
        return found_line

    def have_diff(self):
        c1 = self.get_content_path1()
        c2 = self.get_content_path2()
        return c1.is_binary or c2.is_binary or c1.is_deleted or c2.is_deleted

    def get_diff(self):
        is_new_conflict = ""
        last = ""
        result = ""

        for line in list(
            difflib.unified_diff(
                self.get_content_path1().text, self.get_content_path2().text
            )
        )[2:] + [""]:
            if line.startswith("@@"):
                continue
            if line.startswith("-"):
                if is_new_conflict == "":
                    result += START_DIFF + " Left\n"

                    is_new_conflict = "-"
                elif is_new_conflict == "+" and last == "+":
                    result += BETWEEN_DIFF + "\n"
                last = "-"
                result += line.strip()[1:] + "\n"
            elif line.startswith("+"):
                if is_new_conflict == "":
                    result += START_DIFF + " Right\n"
                    is_new_conflict = "+"
                elif is_new_conflict == "-" and last == "-":
                    result += BETWEEN_DIFF + "\n"
                last = "+"
                result += line.strip()[1:] + "\n"
            else:
                if is_new_conflict == "-":
                    result += END_DIFF + " Right\n"
                elif is_new_conflict == "+":
                    result += END_DIFF + " Left\n"
                last = ""
                is_new_conflict = ""
                result += line.strip() + "\n"

        return Content(result, False, False)
