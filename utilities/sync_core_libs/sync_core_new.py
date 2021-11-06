import json
import os
import shutil
# import threading
from os.path import basename, exists, isdir, join, normpath, relpath
from shutil import copyfile
from typing import List

from deepdiff import DeepDiff

from utilities.conflict import Conflict
from utilities.sync_core_libs.diff_type import DiffType
from utilities.hash import md5
from utilities.sync_core_libs.status_sync_file import StatusSyncFile


class SyncFile:
    def __init__(self, src1, src2, type, status):
        self.src1 = src1
        self.src2 = src2
        self.type = type
        self.status = status

    def get_conflict(self):
        if self.type in [DiffType.AddAddConflict, DiffType.EditEditConflict, DiffType.RemoveEditConflict]:
            return Conflict(self.src1, self.src2, self.type)


class SyncCore:
    SYNC_STRUCT_FILE = ".syncstruct"

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
            added_items = [item.split("[")[-1][1:-2] for item in a['dictionary_item_added'].items]
        if 'dictionary_item_removed' in a:
            removed_items = [item.split("[")[-1][1:-2] for item in a['dictionary_item_removed'].items]
        if 'values_changed' in a:
            edited_items = [key.split("[")[-1][1:-2] for key, value in a['values_changed'].items()]

        return added_items, removed_items, edited_items

    def add_all_as_diff(self, src_dir1, src_dir2):

        struct1 = [f for f in os.listdir(src_dir1)]
        for obj in struct1:
            if basename(obj) == self.SYNC_STRUCT_FILE:
                continue
            new_src1 = join(src_dir1, obj)
            new_src2 = join(src_dir2, obj)
            if isdir(join(src_dir1, obj)):
                self.add_all_as_diff(new_src1, new_src2)
            else:
                o = SyncFile(new_src1, new_src2, None, StatusSyncFile.makeCompare)
                self.diff_list.append(o)
                self.add_file_if_diff(new_src1, new_src2, o)
                # src = relpath(obj, start_dir)
                # result_struct[src] = md5(obj)

        # print("ADD ALL ", src_dir1, src_dir2)

    def get_md5_file_from_sync_file(self, find_src):
        a = relpath(normpath(find_src), self.src_dir1).split("\\")
        b = relpath(normpath(find_src), self.src_dir2).split("\\")
        src_file = (b if len(a) > len(b) else a)
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
        import time

        start = time.time()

        md5_src1 = None
        md5_src2 = None
        if exists(src1):
            md5_src1 = md5(src1)
        end_md5_1 = time.time()
        if exists(src2):
            md5_src2 = md5(src2)
        end_md5_2 = time.time()
        md5_sync_file = self.get_md5_file_from_sync_file(src1)

        if md5_sync_file is None:
            if md5_src1 is not None and md5_src2 is not None:
                self.change_status_diff_list(DiffType.AddAddConflict, diff_list_object)
            elif md5_src1 is not None:
                self.change_status_diff_list(DiffType.Create, diff_list_object)
            else:
                self.change_status_diff_list(DiffType.Create, diff_list_object, True)
        else:
            if md5_sync_file == md5_src1:
                if md5_src2 is None:
                    self.change_status_diff_list(DiffType.Delete, diff_list_object, True)
                elif not md5_sync_file == md5_src2:
                    self.change_status_diff_list(DiffType.Edit, diff_list_object, True)
                else:
                    self.diff_list.remove(diff_list_object)
            elif md5_sync_file == md5_src2:
                if md5_src1 is None:
                    self.change_status_diff_list(DiffType.Delete, diff_list_object)
                elif not md5_sync_file == md5_src1:
                    self.change_status_diff_list(DiffType.Edit, diff_list_object)
            else:
                if md5_src1 is None:
                    self.change_status_diff_list(DiffType.RemoveEditConflict, diff_list_object)
                elif md5_src2 is None:
                    self.change_status_diff_list(DiffType.RemoveEditConflict, diff_list_object, True)
                else:
                    self.change_status_diff_list(DiffType.EditEditConflict, diff_list_object)
            end = time.time()
            print(src1, src2, end - end_md5_2, end_md5_2 - end_md5_1, end_md5_1 - start)

    def generate_structure(self, src_dir1, src_dir2):
        struct1 = [f for f in os.listdir(src_dir1)]
        struct1_copy = struct1.copy()
        struct2 = [f for f in os.listdir(src_dir2)]
        for obj in struct1:
            if basename(obj) == self.SYNC_STRUCT_FILE:
                continue
            new_src1 = join(src_dir1, obj)
            new_src2 = join(src_dir2, obj)
            if isdir(join(src_dir1, obj)):

                if obj in struct2:
                    self.generate_structure(new_src1, new_src2)
                else:
                    self.add_all_as_diff(new_src1, new_src2)
            else:
                o = SyncFile(new_src1, new_src2, None, StatusSyncFile.makeCompare)

                # with self.diff_list_lock:
                self.diff_list.append(o)
                self.add_file_if_diff(new_src1, new_src2, o)
                # add_file_if_diff_thread = threading.Thread(target=self.add_file_if_diff, args=[new_src1, new_src2, o])
                # add_file_if_diff_thread.start()
                # self.add_file_if_diff(new_src1, new_src2, o)
                # src = relpath(obj, start_dir)
                # result_struct[src] = md5(obj)
            if obj in struct2:
                struct2.remove(obj)
            struct1_copy.remove(obj)

        for obj in struct2:
            if basename(obj) == self.SYNC_STRUCT_FILE:
                continue
            new_src1 = join(src_dir1, obj)
            new_src2 = join(src_dir2, obj)
            if isdir(join(src_dir1, obj)):

                if obj in struct1_copy:
                    self.generate_structure(new_src1, new_src2)
                else:
                    self.add_all_as_diff(new_src1, new_src2)
            else:
                o = SyncFile(new_src1, new_src2, None, StatusSyncFile.makeCompare)
                # with self.diff_list_lock:
                #     self.diff_list.append(o)
                self.diff_list.append(o)
                self.add_file_if_diff(new_src1, new_src2, o)
                # add_file_if_diff_thread = threading.Thread(target=self.add_file_if_diff, args=[new_src1, new_src2, o])
                # add_file_if_diff_thread.start()
                # self.add_file_if_diff(new_src1, new_src2, o)
                # src = relpath(obj, start_dir)
                # result_struct[src] = md5(obj)

    def make_diff(self):
        self.make_diff_thread()
        # make_diff_t = threading.Thread(target=self.make_diff_thread)
        # make_diff_t.start()

    def make_diff_thread(self):
        if not exists(join(self.src_dir1, self.SYNC_STRUCT_FILE)):
            with open(join(self.src_dir1, self.SYNC_STRUCT_FILE), 'w') as outfile:
                json.dump({}, outfile)
        with open(join(self.src_dir1, self.SYNC_STRUCT_FILE), 'r') as infile:
            self.sync_file = json.load(infile)
        self.generate_structure(self.src_dir1, self.src_dir2)
        self.is_start = True

    # def compare_dirs(self):
    #     with open(join(self.src_dir1, self.SYNC_STRUCT_FILE), 'r') as infile:
    #         old = json.load(infile)
    #         new1 = self.generate_structure(self.src_dir1)
    #         new2 = self.generate_structure(self.src_dir2)
    #         self.dir1_diff_add, self.dir1_diff_del, self.dir1_diff_edit = self.compare_dictionary(old, new1)
    #         self.dir2_diff_add, self.dir2_diff_del, self.dir2_diff_edit = self.compare_dictionary(old, new2)
    #     print("step 4")

    def update_sync_file(self, diff, is_delete):
        src1 = diff.src1
        src2 = diff.src1

        a = relpath(normpath(src1), self.src_dir1).split("\\")
        b = relpath(normpath(src1), self.src_dir2).split("\\")
        src_file = (b if len(a) > len(b) else a)

        s = src_file[0]
        place = self.sync_file
        for c in src_file[1:]:
            place = place[s]
            s = join(s, c)
            print(s)

        if is_delete:
            del place[s]
        else:
            place[s] = md5(src1)

        print(self.sync_file)
        with open(join(self.src_dir1, self.SYNC_STRUCT_FILE), 'w') as outfile:
            json.dump(self.sync_file, outfile)

    def merge_create_file(self, diff: SyncFile):
        src = diff.src1
        dst = diff.src2
        if isdir(src):
            shutil.copytree(src, dst)
        else:
            copyfile(src, dst)
        self.update_sync_file(diff, False)
        self.diff_list.remove(diff)

    def merge_delete_file(self, diff: SyncFile):
        print(diff)
        if not exists(diff.src2):
            return
        if isdir(diff.src2):
            shutil.rmtree(diff.src2)
        else:
            os.remove(diff.src2)

        self.update_sync_file(diff, True)
        self.diff_list.remove(diff)

    def merge_edit_file(self, diff: SyncFile):
        copyfile(diff.src1, diff.src2)
        self.update_sync_file(diff, False)
        self.diff_list.remove(diff)
        pass

    def merge_with_out_conflict(self, diff: SyncFile):
        diff_type = diff.type
        if diff_type is DiffType.Create:
            self.merge_create_file(diff)
        elif diff_type is DiffType.Delete:
            self.merge_delete_file(diff)
        elif diff_type is DiffType.Edit:
            self.merge_edit_file(diff)
        else:
            raise Exception(str(diff_type) + "is not value of DiffType")

    def resolve_conflict(self, diff, new_content):

        if new_content.is_deleted:
            if exists(diff.src1):
                os.remove(diff.src1)
            if exists(diff.src2):
                os.remove(diff.src2)
        elif new_content.is_binary:
            if new_content.path != diff.src1:
                if exists(diff.src1):
                    os.remove(diff.src1)
                copyfile(new_content.path, diff.src1)
            if new_content.path != diff.src2:
                if exists(diff.src2):
                    os.remove(diff.src2)
                copyfile(new_content.path, diff.src2)
        else:
            with open(diff.src1, "w") as file:
                file.write(new_content.text)

            with open(diff.src2, "w") as file:
                file.write(new_content.text)
        self.update_sync_file(diff, new_content.is_deleted)
