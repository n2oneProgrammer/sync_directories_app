import os
import filecmp
from shutil import copyfile


class SyncCore:
    left_only = []
    right_only = []
    difference_file = []

    def __init__(self, src_dir1, src_dir2):
        self.src_dir1 = src_dir1
        self.src_dir2 = src_dir2

    def compare_dirs(self, src_dir1=None, src_dir2=None):
        if src_dir1 is None:
            src_dir1 = self.src_dir1
        if src_dir2 is None:
            src_dir2 = self.src_dir2
        compare = filecmp.dircmp(src_dir1, src_dir2)
        self.left_only += [os.path.join(src_dir1, src) for src in compare.left_only]
        self.right_only += [os.path.join(src_dir2, src) for src in compare.right_only]
        self.difference_file += [(os.path.join(src_dir1, src), os.path.join(src_dir2, src)) for src in
                                 compare.diff_files]
        for com in compare.common_dirs:
            src1 = os.path.join(self.src_dir1, com)
            src2 = os.path.join(self.src_dir2, com)
            self.compare_dirs(src1, src2)

    def copying_file(self, src_file, to_dir1=False):
        dst_file = os.path.relpath(src_file, self.src_dir2 if to_dir1 else self.src_dir1)
        dst_file = os.path.join(self.src_dir1 if to_dir1 else self.src_dir2, dst_file)
        copyfile(src_file, dst_file)

    def sync_dir(self):
        self.compare_dirs()
        print(self.left_only)
        print(self.right_only)
        for src in self.left_only:
            self.copying_file(src, False)

        for src in self.right_only:
            self.copying_file(src, True)

