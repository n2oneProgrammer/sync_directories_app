import filecmp
import json
import os
import shutil
from os.path import abspath, basename, exists, isdir, isfile, join, relpath
from shutil import copyfile

from deepdiff import DeepDiff

from utilities.errors_type import ConflictsType
from utilities.hash import md5


class SyncCore:
    SYNC_STRUCT_FILE = ".syncstruct"

    left_files_only = []
    right_files_only = []
    left_dirs_only = []
    right_dirs_only = []
    difference_file = []

    def __init__(self, src_dir1, src_dir2):
        self.src_dir1 = src_dir1
        self.src_dir2 = src_dir2

    def add_all_dir(self, src, is_dir1=False):
        onlyfiles = [join(src, f) for f in os.listdir(src) if isfile(join(src, f))]
        onlydirs = [join(src, f) for f in os.listdir(src) if isdir(join(src, f))]
        if is_dir1:
            self.left_files_only += onlyfiles
        else:
            self.right_files_only += onlyfiles
        for d in onlydirs:
            self.add_all_dir(d, is_dir1)

    def compare_dirs(self, src_dir1=None, src_dir2=None):
        if src_dir1 is None:
            src_dir1 = self.src_dir1
        if src_dir2 is None:
            src_dir2 = self.src_dir2
        compare = filecmp.dircmp(src_dir1, src_dir2)
        self.left_files_only += [join(src_dir1, src) for src in compare.left_only if
                                 isfile(abspath(join(src_dir1, src)))]
        self.right_files_only += [join(src_dir2, src) for src in compare.right_only if
                                  isfile(abspath(join(src_dir2, src)))]
        left_dirs = [join(src_dir1, src) for src in compare.left_only if isdir(abspath(join(src_dir1, src)))]
        right_dirs = [join(src_dir2, src) for src in compare.right_only if isdir(abspath(join(src_dir2, src)))]
        self.left_dirs_only += left_dirs
        self.right_dirs_only += right_dirs
        self.difference_file += [(join(src_dir1, src), join(src_dir2, src)) for src in
                                 compare.diff_files]
        for d in left_dirs:
            self.add_all_dir(d, True)

        for d in right_dirs:
            self.add_all_dir(d, False)

        for com in compare.common_dirs:
            src1 = join(self.src_dir1, com)
            src2 = join(self.src_dir2, com)
            self.compare_dirs(src1, src2)

    def generate_structure(self, src_dir, start_dir=None):
        result_struct = {}
        if start_dir is None:
            start_dir = src_dir
        struct = [join(src_dir, f) for f in os.listdir(src_dir)]
        for obj in struct:
            if basename(obj) == self.SYNC_STRUCT_FILE:
                continue
            if isdir(obj):
                src = relpath(obj, start_dir)
                result_struct[src] = self.generate_structure(obj, start_dir)
            else:
                src = relpath(obj, start_dir)
                result_struct[src] = md5(obj)
        return result_struct

    @staticmethod
    def compare_dictionary(old_dictionary, new_dictionary):
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

    def sync_dir(self):
        if not exists(join(self.src_dir1, self.SYNC_STRUCT_FILE)):
            dir_struct = self.generate_structure(self.src_dir1)
            with open(join(self.src_dir1, self.SYNC_STRUCT_FILE), 'w') as outfile:
                json.dump(dir_struct, outfile)

        with open(join(self.src_dir1, self.SYNC_STRUCT_FILE), 'r') as infile:
            old = json.load(infile)
            new = self.generate_structure(self.src_dir1)
            dir1_diff_add, dir1_diff_del, dir1_diff_edit = SyncCore.compare_dictionary(old, new)

        with open(join(self.src_dir1, self.SYNC_STRUCT_FILE), 'r') as infile:
            old = json.load(infile)
            new = self.generate_structure(self.src_dir2)
            dir2_diff_add, dir2_diff_del, dir2_diff_edit = SyncCore.compare_dictionary(old, new)
        print(dir1_diff_add, dir1_diff_del, dir1_diff_edit)
        print(dir2_diff_add, dir2_diff_del, dir2_diff_edit)
        conflicts_tab = []

        conflicts_tab.extend(self.generate_added_dir_file(dir1_diff_add, dir2_diff_add, False))
        conflicts_tab.extend(self.generate_added_dir_file(dir2_diff_add, dir1_diff_add, True))

        conflicts_tab.extend(self.removing_deleted_dir_file(dir1_diff_del, dir2_diff_edit, False))
        conflicts_tab.extend(self.removing_deleted_dir_file(dir2_diff_del, dir1_diff_edit, True))

        conflicts_tab.extend(self.editing_dir_file(dir1_diff_edit, dir2_diff_edit, False))
        conflicts_tab.extend(self.editing_dir_file(dir2_diff_edit, dir1_diff_edit, True))

        print(conflicts_tab)

        dir_struct = self.generate_structure(self.src_dir1)
        with open(join(self.src_dir1, self.SYNC_STRUCT_FILE), 'w') as outfile:
            json.dump(dir_struct, outfile)

        return conflicts_tab

    def generate_added_dir_file(self, diff1, diff2, revers=False):
        result_conflicts = []
        for d in diff1:
            diff1.remove(d)
            if revers:
                src = join(self.src_dir2, d)
                dst = join(self.src_dir1, d)
            else:
                src = join(self.src_dir1, d)
                dst = join(self.src_dir2, d)
            if d in diff2:
                diff2.remove(d)
                result_conflicts.append({
                    "left": src,
                    "right": dst,
                    "type": ConflictsType.AddAdd
                })
                print("ERROR I dont know what i should do with " + d)
            else:

                if isdir(src):
                    shutil.copytree(src, dst)
                else:
                    copyfile(src, dst)
        return result_conflicts

    def removing_deleted_dir_file(self, remove1, edit2, revers=False):
        result_conflicts = []
        for r in remove1:
            remove1.remove(r)
            if revers:
                src = join(self.src_dir2, r)
                target = join(self.src_dir1, r)
            else:
                src = join(self.src_dir2, r)
                target = join(self.src_dir2, r)
            if r in edit2:
                edit2.remove(r)
                result_conflicts.append({
                    "left": src,
                    "right": target,
                    "type": ConflictsType.RemoveEdit
                })
                print("ERROR I dont know what i should do with " + r)
            else:
                if isdir(src):
                    shutil.rmtree(target)
                else:
                    os.remove(target)
        return result_conflicts

    def editing_dir_file(self, edit1, edit2, revers=False):
        result_conflicts = []
        for r in edit1:
            edit1.remove(r)
            if revers:
                src = join(self.src_dir2, r)
                dst = join(self.src_dir1, r)
            else:
                src = join(self.src_dir2, r)
                dst = join(self.src_dir2, r)
            if r in edit2:
                edit2.remove(r)
                result_conflicts.append({
                    "left": src,
                    "right": dst,
                    "type": ConflictsType.EditEdit
                })
                print("ERROR I dont know what i should do with " + r)
            else:
                copyfile(src, dst)

        return result_conflicts
