import json
import os
import shutil
from copy import deepcopy
from os.path import basename, dirname, join, normpath, relpath
from pathlib import Path
from shutil import copy2

import win32api
# import threading
import win32con
from deepdiff import DeepDiff
from utilities.hash import Hash
from utilities.settings import Settings
from utilities.sync_core_libs.diff_type import DiffType
from utilities.sync_core_libs.ignore_file import IgnoreFile
from utilities.sync_core_libs.status_sync_file import StatusSyncFile
from utilities.sync_core_libs.sync_file import SyncFile


class SyncCore:
    def __init__(self, src_dir1, src_dir2):
        self.src_dir1 = src_dir1
        self.src_dir2 = src_dir2
        self.dir1_diff_add = []
        self.dir1_diff_del = []
        self.dir1_diff_edit = []

        self.dir2_diff_add = []
        self.dir2_diff_del = []
        self.dir2_diff_edit = []

        self.diff_list = []

        self.ignore_file = IgnoreFile(src_dir1)

        # self.diff_list_lock = threading.Lock()
        self.sync_file = {}
        self.is_start = False
        self.make_diff()

    def compare_dictionary(self, old_dictionary, new_dictionary):
        a = DeepDiff(old_dictionary, new_dictionary)
        added_items = []
        removed_items = []
        edited_items = []
        if "dictionary_item_added" in a:
            added_items = [
                item.split("[")[-1][1:-2] for item in a["dictionary_item_added"].items
            ]
        if "dictionary_item_removed" in a:
            removed_items = [
                item.split("[")[-1][1:-2] for item in a["dictionary_item_removed"].items
            ]
        if "values_changed" in a:
            edited_items = [
                key.split("[")[-1][1:-2] for key, value in a["values_changed"].items()
            ]

        return added_items, removed_items, edited_items

    def add_all_as_diff(self, src_dir1, src_dir2):

        struct1 = [f for f in os.listdir(src_dir1)]
        for obj in struct1:
            if basename(obj) == Settings().get("sync_struct_file_name"):
                continue

            new_src1 = join(src_dir1, obj)
            new_src2 = join(src_dir2, obj)
            if self.ignore_file.is_detect(relpath(new_src1, self.src_dir1)):
                continue
            if os.path.isdir(join(src_dir1, obj)):
                o = SyncFile(new_src1, new_src2, None, StatusSyncFile.makeCompare)
                # with self.diff_list_lock:
                self.diff_list.append(o)

                self.add_dir_if_diff(new_src1, new_src2, o)
                self.add_all_as_diff(new_src1, new_src2)
            else:
                o = SyncFile(new_src1, new_src2, None, StatusSyncFile.makeCompare)
                self.diff_list.append(o)
                self.add_file_if_diff(new_src1, new_src2, o)

    def get_md5_file_from_sync_file(self, find_src):
        try:
            a = relpath(normpath(find_src), self.src_dir1).split("\\")
        except ValueError:
            a = None
        try:
            b = relpath(normpath(find_src), self.src_dir2).split("\\")
        except ValueError:
            b = None

        if a is None:
            src_file = b
        elif b is None:
            src_file = a
        else:
            src_file = b if len(a) > len(b) else a

        s = src_file[0]
        place = self.sync_file
        for c in src_file[1:]:
            if not s in place:
                return None
            place = place[s]
            s = join(s, c)
        if s in place:
            return place[s]
        else:
            return None

    def change_status_diff_list(self, type, diff_list_object, reverse_src=False):
        if reverse_src:
            temp_src = diff_list_object.src1
            diff_list_object.src1 = diff_list_object.src2
            diff_list_object.src2 = temp_src
        diff_list_object.status = StatusSyncFile.finalCompare
        diff_list_object.type = type

    def is_all_compare(self):
        if not self.is_start:
            return False
        for obj in self.diff_list:
            if obj.status == StatusSyncFile.makeCompare:
                return False
        return True

    def add_file_if_diff(self, src1, src2, diff_list_object):
        md5_src1 = None
        md5_src2 = None
        limit_hash = Settings().get("limit_hashing_file_MB")
        hash = None
        md5_sync_file = self.get_md5_file_from_sync_file(src1)
        if md5_sync_file is not None:
            limit_hash = md5_sync_file["limit"]
            hash = md5_sync_file["hash"]
        if os.path.exists(src1):
            md5_src1 = Hash.md5(src1, limit_hash)
        if os.path.exists(src2):
            md5_src2 = Hash.md5(src2, limit_hash)

        if hash is None:
            if md5_src1 is not None and md5_src2 is not None:
                self.change_status_diff_list(DiffType.AddAddConflict, diff_list_object)
            elif md5_src1 is not None:
                self.change_status_diff_list(DiffType.Create, diff_list_object)
            else:
                self.change_status_diff_list(DiffType.Create, diff_list_object, True)
        else:
            if hash == md5_src1:
                if md5_src2 is None:
                    self.change_status_diff_list(
                        DiffType.Delete, diff_list_object, True
                    )
                elif not hash == md5_src2:
                    self.change_status_diff_list(DiffType.Edit, diff_list_object, True)
                else:
                    self.update_sync_file(diff_list_object, False)
                    self.diff_list.remove(diff_list_object)
            elif hash == md5_src2:
                if md5_src1 is None:
                    self.change_status_diff_list(DiffType.Delete, diff_list_object)
                elif not hash == md5_src1:
                    self.change_status_diff_list(DiffType.Edit, diff_list_object)
            else:
                if md5_src1 is None:
                    if md5_src2 is None:
                        self.change_status_diff_list(
                            DiffType.RemoveRemove, diff_list_object
                        )
                    else:
                        self.change_status_diff_list(
                            DiffType.RemoveEditConflict, diff_list_object
                        )
                elif md5_src2 is None:
                    self.change_status_diff_list(
                        DiffType.RemoveEditConflict, diff_list_object, True
                    )
                else:
                    self.change_status_diff_list(
                        DiffType.EditEditConflict, diff_list_object
                    )

    def add_dir_if_diff(self, src1, src2, diff_list_object):
        is_hidden1 = False
        is_hidden2 = False
        if os.path.exists(src1):
            status = win32api.GetFileAttributes(src1)
            is_hidden1 = not status & win32con.FILE_ATTRIBUTE_HIDDEN == 0
        if os.path.exists(src2):
            status2 = win32api.GetFileAttributes(src2)
            is_hidden2 = not status2 & win32con.FILE_ATTRIBUTE_HIDDEN == 0
        if is_hidden1:
            self.change_status_diff_list(DiffType.Create, diff_list_object)
        if is_hidden2:
            self.change_status_diff_list(DiffType.Create, diff_list_object, True)
        else:
            self.diff_list.remove(diff_list_object)

    def find_dir_in_sync_file(self, sync_file, dir_name):
        for key in sync_file.keys():
            if normpath(key).split("\\")[-1] == dir_name:
                return key
        return None

    def generate_structure(self, src_dir1, src_dir2, sync_file_state=None):
        if sync_file_state is None:
            sync_file_state = deepcopy(self.sync_file)
        struct1 = [f for f in os.listdir(src_dir1)]
        struct1_copy = struct1.copy()
        struct2 = [f for f in os.listdir(src_dir2)]
        for obj in struct1:

            if basename(obj) == Settings().get("sync_struct_file_name"):
                continue

            new_src1 = join(src_dir1, obj)
            new_src2 = join(src_dir2, obj)

            if self.ignore_file.is_detect(relpath(new_src1, self.src_dir1)):
                continue
            sync_dir = self.find_dir_in_sync_file(sync_file_state, obj)
            if os.path.isdir(join(src_dir1, obj)):
                if obj in struct2:
                    if sync_dir is not None:
                        sub_dir = sync_file_state[sync_dir]
                    else:
                        sub_dir = {}
                    o = SyncFile(new_src1, new_src2, None, StatusSyncFile.makeCompare)
                    # with self.diff_list_lock:
                    self.diff_list.append(o)

                    self.add_dir_if_diff(new_src1, new_src2, o)
                    self.generate_structure(new_src1, new_src2, sub_dir)
                    if sync_dir is not None:
                        del sync_file_state[sync_dir]
                else:
                    if sync_dir is not None:
                        del sync_file_state[sync_dir]
                    o = SyncFile(new_src1, new_src2, None, StatusSyncFile.makeCompare)
                    # with self.diff_list_lock:
                    self.diff_list.append(o)

                    self.add_dir_if_diff(new_src1, new_src2, o)
                    self.add_all_as_diff(new_src1, new_src2)
            else:
                o = SyncFile(new_src1, new_src2, None, StatusSyncFile.makeCompare)

                # with self.diff_list_lock:
                self.diff_list.append(o)
                if sync_dir is not None:
                    del sync_file_state[sync_dir]
                self.add_file_if_diff(new_src1, new_src2, o)
                # add_file_if_diff_thread = threading.Thread(target=self.add_file_if_diff, args=[new_src1, new_src2, o])
                # add_file_if_diff_thread.start()
            if obj in struct2:
                struct2.remove(obj)
            struct1_copy.remove(obj)

        for obj in struct2:
            if basename(obj) == Settings().get("sync_struct_file_name"):
                continue

            new_src1 = join(src_dir1, obj)
            new_src2 = join(src_dir2, obj)
            sync_dir = self.find_dir_in_sync_file(sync_file_state, obj)
            if os.path.isdir(join(src_dir1, obj)):

                if obj in struct1_copy:
                    if sync_dir is not None:
                        sub_dir = sync_file_state[sync_dir]
                    else:
                        sub_dir = {}

                    o = SyncFile(new_src1, new_src2, None, StatusSyncFile.makeCompare)
                    # with self.diff_list_lock:
                    self.diff_list.append(o)

                    self.add_dir_if_diff(new_src1, new_src2, o)
                    self.generate_structure(new_src1, new_src2, sub_dir)
                else:
                    del sync_file_state[sync_dir]
                    self.add_all_as_diff(new_src1, new_src2)
            else:
                if os.path.isdir(join(src_dir2, obj)):
                    if sync_dir is not None:
                        del sync_file_state[sync_dir]
                    o = SyncFile(new_src1, new_src2, None, StatusSyncFile.makeCompare)
                    # with self.diff_list_lock:
                    self.diff_list.append(o)

                    self.add_dir_if_diff(new_src1, new_src2, o)
                    self.add_all_as_diff(new_src2, new_src1)
                else:
                    o = SyncFile(new_src1, new_src2, None, StatusSyncFile.makeCompare)
                    # with self.diff_list_lock:
                    #     self.diff_list.append(o)
                    self.diff_list.append(o)
                    if sync_dir is not None:
                        del sync_file_state[sync_dir]
                    self.add_file_if_diff(new_src1, new_src2, o)
                # add_file_if_diff_thread = threading.Thread(target=self.add_file_if_diff, args=[new_src1, new_src2, o])
                # add_file_if_diff_thread.start()
        for obj in sync_file_state.copy().keys():
            new_src1 = join(src_dir1, obj)
            new_src2 = join(src_dir2, obj)

            o = SyncFile(new_src1, new_src2, None, StatusSyncFile.makeCompare)
            # with self.diff_list_lock:
            #     self.diff_list.append(o)
            self.diff_list.append(o)
            self.add_file_if_diff(new_src1, new_src2, o)
            del sync_file_state[obj]
            # add_file_if_diff_thread = threading.Thread(target=

    def make_diff(self):
        self.make_diff_thread()
        # make_diff_t = threading.Thread(target=self.make_diff_thread)
        # make_diff_t.start()

    def make_diff_thread(self):
        if not os.path.exists(
            join(self.src_dir1, Settings().get("sync_struct_file_name"))
        ):
            with open(
                join(self.src_dir1, Settings().get("sync_struct_file_name")), "w"
            ) as outfile:
                json.dump({}, outfile)
        with open(
            join(self.src_dir1, Settings().get("sync_struct_file_name")), "r"
        ) as infile:
            self.sync_file = json.load(infile)
        self.generate_structure(self.src_dir1, self.src_dir2)
        self.is_start = True

    def update_sync_file(self, diff, is_delete):
        src1 = diff.src1

        try:
            a = relpath(normpath(src1), self.src_dir1).split("\\")
        except ValueError:
            a = None
        try:
            b = relpath(normpath(src1), self.src_dir2).split("\\")
        except ValueError:
            b = None

        if a is None:
            src_file = b
        elif b is None:
            src_file = a
        else:
            src_file = b if len(a) > len(b) else a
        s = src_file[0]
        place = self.sync_file
        for c in src_file[1:]:
            if s in place:
                place = place[s]
            else:
                place[s] = {}
                place = place[s]
            s = join(s, c)

        if is_delete:
            del place[s]
        else:
            if not os.path.isdir(src1):
                place[s] = {
                    "limit": Settings().get("limit_hashing_file_MB"),
                    "hash": Hash.md5(src1),
                }

        with open(
            join(self.src_dir1, Settings().get("sync_struct_file_name")), "w"
        ) as outfile:
            json.dump(self.sync_file, outfile)

    def merge_create_file(self, diff: SyncFile):
        src = diff.src1
        dst = diff.src2
        if os.path.isdir(src):
            Path(dst).mkdir(parents=True, exist_ok=True)
            win32api.SetFileAttributes(dst, win32con.FILE_ATTRIBUTE_HIDDEN)
        else:
            Path(dirname(dst)).mkdir(parents=True, exist_ok=True)
            copy2(src, dst)
            win32api.SetFileAttributes(dst, win32api.GetFileAttributes(src))
        self.update_sync_file(diff, False)
        self.diff_list.remove(diff)

    def merge_delete_file(self, diff: SyncFile):
        if not os.path.exists(diff.src2):
            return
        if os.path.isdir(diff.src2):
            shutil.rmtree(diff.src2)
        else:
            os.remove(diff.src2)

        self.update_sync_file(diff, True)
        self.diff_list.remove(diff)

    def merge_removeremove_file(self, diff: SyncFile):
        self.update_sync_file(diff, True)
        self.diff_list.remove(diff)

    def merge_edit_file(self, diff: SyncFile):
        copy2(diff.src1, diff.src2)
        self.update_sync_file(diff, False)
        self.diff_list.remove(diff)

    def merge_with_out_conflict(self, diff: SyncFile):
        diff_type = diff.type
        if diff_type is DiffType.Create:
            self.merge_create_file(diff)
        elif diff_type is DiffType.Delete:
            self.merge_delete_file(diff)
        elif diff_type is DiffType.Edit:
            self.merge_edit_file(diff)
        elif diff_type is DiffType.RemoveRemove:
            self.merge_removeremove_file(diff)
        else:
            raise Exception(str(diff_type) + "is not value of DiffType")

    def resolve_conflict(self, diff, new_content):

        if new_content.is_deleted:
            if os.path.exists(diff.src1):
                os.remove(diff.src1)
            if os.path.exists(diff.src2):
                os.remove(diff.src2)
        elif new_content.is_binary:
            if new_content.path != diff.src1:
                if os.path.exists(diff.src1):
                    os.remove(diff.src1)
                copy2(new_content.path, diff.src1)
            if new_content.path != diff.src2:
                if os.path.exists(diff.src2):
                    os.remove(diff.src2)
                copy2(new_content.path, diff.src2)
        else:
            with open(diff.src1, "w") as file:
                file.write(new_content.text)

            with open(diff.src2, "w") as file:
                file.write(new_content.text)
        self.update_sync_file(diff, new_content.is_deleted)
