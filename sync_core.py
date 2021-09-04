import os
from os.path import join, isfile, isdir, abspath, relpath
import filecmp
from shutil import copyfile


class SyncCore:
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

    def creating_dirs(self, src_dir, to_dir1=False):
        path_dir = relpath(src_dir, self.src_dir2 if to_dir1 else self.src_dir1)
        path_dir = join(self.src_dir1 if to_dir1 else self.src_dir2, path_dir)

        os.makedirs(path_dir)

    def copying_file(self, src_file, to_dir1=False):
        dst_file = relpath(src_file, self.src_dir2 if to_dir1 else self.src_dir1)
        dst_file = join(self.src_dir1 if to_dir1 else self.src_dir2, dst_file)
        copyfile(src_file, dst_file)

    def sync_dir(self):
        self.compare_dirs()
        print(self.left_files_only)
        print(self.right_files_only)
        print(self.left_dirs_only)
        print(self.right_dirs_only)

        for src in self.left_dirs_only:
            self.creating_dirs(src, False)

        for src in self.right_dirs_only:
            self.creating_dirs(src, True)

        for src in self.left_files_only:
            self.copying_file(src, False)

        for src in self.right_files_only:
            self.copying_file(src, True)
