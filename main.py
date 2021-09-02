import sys
import os
import filecmp

left_only = []
right_only = []
difference_file = []


def compare_dirs(src_dir1, src_dir2):
    global left_only, right_only, difference_file
    compare = filecmp.dircmp(src_dir1, src_dir2)
    left_only += [os.path.join(src_dir1, src) for src in compare.left_only]
    right_only += [os.path.join(src_dir2, src) for src in compare.right_only]
    difference_file += [(os.path.join(src_dir1, src), os.path.join(src_dir2, src)) for src in compare.diff_files]
    for com in compare.common_dirs:
        src1 = os.path.join(src_dir1, com)
        src2 = os.path.join(src_dir2, com)
        compare_dirs(src1, src2)


if __name__ == "__main__":
    dirs = sys.argv[1:3]
    compare_dirs(dirs[0], dirs[1])
    print(left_only)
    print(right_only)
    print(difference_file)
