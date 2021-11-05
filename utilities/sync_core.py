import json
import os
import shutil
from os.path import basename, exists, isdir, join, normpath, relpath
from shutil import copyfile
from typing import List

from deepdiff import DeepDiff

from utilities.conflict import Conflict
from utilities.sync_core_libs.diff_type import DiffType
from utilities.hash import md5


class SyncCore:
    SYNC_STRUCT_FILE = ".syncstruct"

    def __init__(self, src_dir1, src_dir2):
        self.src_dir1 = src_dir1
        self.src_dir2 = src_dir2

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

    @staticmethod
    def include_conflict_tab(conflicts: List[Conflict], path):
        for conflict in conflicts:
            if conflict.path1 == path:
                return conflict.type
            if conflict.path2 == path:
                return conflict.type
        return None

    def generate_structure_with_conflicts(self, src_dir, conflicts: List[Conflict], old_structure, start_dir=None):
        result_struct = {}
        if start_dir is None:
            start_dir = src_dir
        struct = [normpath(join(src_dir, f)) for f in os.listdir(src_dir)]
        for obj in struct:
            if basename(obj) == self.SYNC_STRUCT_FILE:
                continue
            conflicts_type = self.include_conflict_tab(conflicts, obj)
            src = relpath(obj, start_dir)
            if conflicts_type is not None:
                if conflicts_type != DiffType.AddAddConflict:
                    result_struct[src] = old_structure[src]
            elif isdir(obj):
                if src in old_structure:
                    result_struct[src] = self.generate_structure_with_conflicts(obj,
                                                                                conflicts,
                                                                                old_structure[src],
                                                                                start_dir)
                else:
                    result_struct[src] = self.generate_structure(obj, start_dir)
            else:
                result_struct[src] = md5(obj)

        removing_elements_in_dir1_tab = [a.path1 for a in conflicts if a.type == DiffType.RemoveEditConflict]
        for element in removing_elements_in_dir1_tab:
            key = relpath(element, start_dir)
            if relpath(element, src_dir) == basename(element):
                result_struct[key] = old_structure[key]

        return result_struct

    def sync_dir(self):
        if not exists(join(self.src_dir1, self.SYNC_STRUCT_FILE)):
            with open(join(self.src_dir1, self.SYNC_STRUCT_FILE), 'w') as outfile:
                json.dump({}, outfile)

        with open(join(self.src_dir1, self.SYNC_STRUCT_FILE), 'r') as infile:
            old = json.load(infile)
            new1 = self.generate_structure(self.src_dir1)
            new2 = self.generate_structure(self.src_dir2)
            dir1_diff_add, dir1_diff_del, dir1_diff_edit = SyncCore.compare_dictionary(old, new1)
            dir2_diff_add, dir2_diff_del, dir2_diff_edit = SyncCore.compare_dictionary(old, new2)
        print(dir1_diff_add, dir1_diff_del, dir1_diff_edit)
        print(dir2_diff_add, dir2_diff_del, dir2_diff_edit)

        conflicts_tab: List[Conflict] = []

        conflicts_tab.extend(self.generate_added_dir_file(dir1_diff_add, dir2_diff_add, False))
        conflicts_tab.extend(self.generate_added_dir_file(dir2_diff_add, dir1_diff_add, True))

        conflicts_tab.extend(self.removing_deleted_dir_file(dir1_diff_del, dir2_diff_edit, False))
        conflicts_tab.extend(self.removing_deleted_dir_file(dir2_diff_del, dir1_diff_edit, True))

        conflicts_tab.extend(self.editing_dir_file(dir1_diff_edit, dir2_diff_edit, False))
        conflicts_tab.extend(self.editing_dir_file(dir2_diff_edit, dir1_diff_edit, True))

        resulting_conf_tab = []

        for conf in conflicts_tab:
            resulting_conf_tab.extend(self.resolve_simple_conflicts(conf))

        dir_struct = self.generate_structure_with_conflicts(self.src_dir1, resulting_conf_tab, old)
        with open(join(self.src_dir1, self.SYNC_STRUCT_FILE), 'w') as outfile:
            json.dump(dir_struct, outfile)

        return resulting_conf_tab

    def generate_added_dir_file(self, diff1, diff2, revers=False) -> List[Conflict]:
        result_conflicts: List[Conflict] = []
        copy_diff1 = diff1.copy()
        for d in copy_diff1:
            diff1.remove(d)
            if revers:
                src = join(self.src_dir2, d)
                dst = join(self.src_dir1, d)
            else:
                src = join(self.src_dir1, d)
                dst = join(self.src_dir2, d)

            if d in diff2:
                diff2.remove(d)
                result_conflicts.append(Conflict(src, dst, DiffType.AddAddConflict))
                print("ERROR I dont know what i should do with " + d)
            else:
                if isdir(src):
                    shutil.copytree(src, dst)
                else:
                    copyfile(src, dst)

        return result_conflicts

    def removing_deleted_dir_file(self, remove1, edit2, revers=False) -> List[Conflict]:
        result_conflicts: List[Conflict] = []
        copy_remove1 = remove1.copy()
        for r in copy_remove1:
            remove1.remove(r)
            if revers:
                src = join(self.src_dir2, r)
                target = join(self.src_dir1, r)
            else:
                src = join(self.src_dir1, r)
                target = join(self.src_dir2, r)
            if r in edit2:
                edit2.remove(r)
                result_conflicts.append(Conflict(src, target, DiffType.RemoveEditConflict))
                print("ERROR I dont know what i should do with " + r)
            else:
                if not exists(target):
                    continue
                if isdir(target):
                    shutil.rmtree(target)
                else:
                    os.remove(target)
        return result_conflicts

    def editing_dir_file(self, edit1, edit2, revers=False) -> List[Conflict]:
        result_conflicts = []
        copy_edit1 = edit1.copy()
        for r in copy_edit1:
            edit1.remove(r)
            if revers:
                src = join(self.src_dir2, r)
                dst = join(self.src_dir1, r)
            else:
                src = join(self.src_dir1, r)
                dst = join(self.src_dir2, r)
            if r in edit2:
                edit2.remove(r)
                result_conflicts.append(Conflict(src, dst, DiffType.EditEditConflict))
                print("ERROR I dont know what i should do with " + r)
            else:
                copyfile(src, dst)

        return result_conflicts

    def resolve_simple_conflicts(self, conflict: Conflict):
        path1 = conflict.path1
        path2 = conflict.path2
        conflicts = []
        if isdir(path1):
            if conflict.type == DiffType.AddAddConflict:
                dir1 = self.generate_structure(path1)
                dir2 = self.generate_structure(path2)
                diff_add, diff_del, diff_edit = SyncCore.compare_dictionary(dir1, dir2)
                for add in diff_add:
                    src = join(path2, add)
                    dst = join(path1, add)
                    if isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        copyfile(src, dst)
                for add in diff_del:
                    src = join(path1, add)
                    dst = join(path2, add)
                    if isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        copyfile(src, dst)

                for edit in diff_edit:
                    conflicts.append(Conflict(join(path1, edit), join(path2, edit), DiffType.AddAddConflict))
        else:
            conflicts.append(conflict)
        return conflicts

    def resolve_conflict(self, src1, src2, new_content):
        if new_content.is_deleted:
            if exists(src1):
                os.remove(src1)
            if exists(src2):
                os.remove(src2)
        elif new_content.is_binary:
            if new_content.path != src1:
                if exists(src1):
                    os.remove(src1)
                copyfile(new_content.path, src1)
            if new_content.path != src2:
                if exists(src2):
                    os.remove(src2)
                copyfile(new_content.path, src2)
        else:
            with open(src1, "w") as file:
                file.write(new_content.text)

            with open(src2, "w") as file:
                file.write(new_content.text)

        a = relpath(normpath(src1), self.src_dir1).split("\\")
        b = relpath(normpath(src1), self.src_dir2).split("\\")
        src_file = (b if len(a) > len(b) else a)

        with open(join(self.src_dir1, self.SYNC_STRUCT_FILE), 'r') as infile:
            sync_file = json.load(infile)

            s = src_file[0]
            place = sync_file
            for c in src_file[1:]:
                place = place[s]
                s = join(s, c)
                print(s)
            if new_content.is_deleted:
                del place[s]
            else:
                place[s] = md5(src1)

            print(sync_file)
        with open(join(self.src_dir1, self.SYNC_STRUCT_FILE), 'w') as outfile:
            json.dump(sync_file, outfile)
