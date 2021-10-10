import filecmp
import os
import shutil

from utilities.conflict import Conflict
from utilities.conflict_resolver.conflict_resolver_file import ConflictResolverFile
from utilities.sync_core import SyncCore

TEST_DIR = "../test_data"
TEST_DIR_A = os.path.join(TEST_DIR, "a")
TEST_DIR_B = os.path.join(TEST_DIR, "b")


def clean():
    for filename in os.listdir(TEST_DIR):
        file_path = os.path.join(TEST_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    os.mkdir(TEST_DIR_A)
    os.mkdir(TEST_DIR_B)


def are_dir_trees_equal(dir1, dir2):
    dirs_cmp = filecmp.dircmp(dir1, dir2)
    left_only = dirs_cmp.left_only
    if ".syncstruct" in left_only:
        left_only.remove(".syncstruct")
    right_only = dirs_cmp.right_only
    if ".syncstruct" in right_only:
        right_only.remove(".syncstruct")
    if len(left_only) > 0 or len(right_only) > 0 or \
            len(dirs_cmp.funny_files) > 0:
        return False
    (_, mismatch, errors) = filecmp.cmpfiles(
        dir1, dir2, dirs_cmp.common_files, shallow=False)
    if len(mismatch) > 0 or len(errors) > 0:
        return False
    for common_dir in dirs_cmp.common_dirs:
        new_dir1 = os.path.join(dir1, common_dir)
        new_dir2 = os.path.join(dir2, common_dir)
        if not are_dir_trees_equal(new_dir1, new_dir2):
            return False
    return True


def create_struct(struct, dir=None):
    if dir is None:
        dir = TEST_DIR
    for key in list(struct.keys()):
        obj = struct[key]
        src = os.path.join(dir, key)
        if type(obj) is str:
            create_file(src, obj)
        else:
            os.mkdir(src)
            create_struct(obj, src)


def copy_a2b():
    clean()
    create_struct({
        "a": {
            "b": {
                "c.json": "zaq1"
            }
        }

    }, TEST_DIR_A)
    sync_core = SyncCore(TEST_DIR_A, TEST_DIR_B)
    sync_core.sync_dir()
    assert are_dir_trees_equal(TEST_DIR_A, TEST_DIR_B) is True


def create_file(src, content):
    with open(src, "w") as f:
        f.write(content)


def copy_b2a():
    clean()
    create_struct({
        "a": {
            "b": {
                "c.json": "zaq1"
            }
        }

    }, TEST_DIR_B)
    sync_core = SyncCore(TEST_DIR_A, TEST_DIR_B)
    sync_core.sync_dir()
    assert are_dir_trees_equal(TEST_DIR_A, TEST_DIR_B) is True


def copy_a_and_b():
    clean()
    create_struct({
        "a": {
            "b": {
                "c.json": "zaq1"
            }
        }

    }, TEST_DIR_A)
    create_struct({
        "c": {
            "d": {
                "f.json": "zaq1"
            }
        }

    }, TEST_DIR_B)
    sync_core = SyncCore(TEST_DIR_A, TEST_DIR_B)
    sync_core.sync_dir()
    assert are_dir_trees_equal(TEST_DIR_A, TEST_DIR_B) is True


def copy_add_add_file():
    copy_a_and_b()
    sync_core = SyncCore(TEST_DIR_A, TEST_DIR_B)
    create_file(os.path.join(TEST_DIR_A, "a", "b", "test"), "zaq1")
    create_file(os.path.join(TEST_DIR_B, "a", "b", "test"), "mkop")
    sync = sync_core.sync_dir()
    assert len(sync) == 1
    assert type(sync[0]) is Conflict
    con = ConflictResolverFile(sync[0], sync_core)
    con.resolve("test")
    assert are_dir_trees_equal(TEST_DIR_A, TEST_DIR_B) is True


def copy_remove_remove_file():
    copy_a_and_b()
    sync_core = SyncCore(TEST_DIR_A, TEST_DIR_B)
    os.remove(os.path.join(TEST_DIR_A, "a", "b", "c.json"))
    os.remove(os.path.join(TEST_DIR_B, "a", "b", "c.json"))
    sync = sync_core.sync_dir()
    assert len(sync) == 0
    assert are_dir_trees_equal(TEST_DIR_A, TEST_DIR_B) is True


def copy_remove_edit_file_remove():
    copy_a_and_b()
    sync_core = SyncCore(TEST_DIR_A, TEST_DIR_B)
    os.remove(os.path.join(TEST_DIR_A, "a", "b", "c.json"))
    with open(os.path.join(TEST_DIR_B, "a", "b", "c.json"), "w") as f:
        f.write("new text")
    sync = sync_core.sync_dir()
    assert len(sync) == 1
    assert type(sync[0]) is Conflict
    con = ConflictResolverFile(sync[0], sync_core)
    con.resolve("test")
    assert are_dir_trees_equal(TEST_DIR_A, TEST_DIR_B) is True


def copy_remove_edit_file_delete():
    copy_a_and_b()
    sync_core = SyncCore(TEST_DIR_A, TEST_DIR_B)
    os.remove(os.path.join(TEST_DIR_A, "a", "b", "c.json"))
    with open(os.path.join(TEST_DIR_B, "a", "b", "c.json"), "w") as f:
        f.write("new text")
    sync = sync_core.sync_dir()
    assert len(sync) == 1
    assert type(sync[0]) is Conflict
    con = ConflictResolverFile(sync[0], sync_core)
    con.resolve(None)
    assert are_dir_trees_equal(TEST_DIR_A, TEST_DIR_B) is True


def copy_edit_remove_file_remove():
    copy_a_and_b()
    sync_core = SyncCore(TEST_DIR_A, TEST_DIR_B)
    os.remove(os.path.join(TEST_DIR_B, "a", "b", "c.json"))
    with open(os.path.join(TEST_DIR_A, "a", "b", "c.json"), "w") as f:
        f.write("new text")
    sync = sync_core.sync_dir()
    assert len(sync) == 1
    assert type(sync[0]) is Conflict
    con = ConflictResolverFile(sync[0], sync_core)
    con.resolve("test")
    assert are_dir_trees_equal(TEST_DIR_A, TEST_DIR_B) is True


def copy_edit_remove_file_delete():
    copy_a_and_b()
    sync_core = SyncCore(TEST_DIR_A, TEST_DIR_B)
    os.remove(os.path.join(TEST_DIR_B, "a", "b", "c.json"))
    with open(os.path.join(TEST_DIR_A, "a", "b", "c.json"), "w") as f:
        f.write("new text")
    sync = sync_core.sync_dir()
    assert len(sync) == 1
    assert type(sync[0]) is Conflict
    con = ConflictResolverFile(sync[0], sync_core)
    con.resolve(None)
    assert are_dir_trees_equal(TEST_DIR_A, TEST_DIR_B) is True


def copy_edit_edit_file():
    copy_a_and_b()
    sync_core = SyncCore(TEST_DIR_A, TEST_DIR_B)
    with open(os.path.join(TEST_DIR_B, "a", "b", "c.json"), "w") as f:
        f.write("new text2")

    with open(os.path.join(TEST_DIR_A, "a", "b", "c.json"), "w") as f:
        f.write("new text")
    sync = sync_core.sync_dir()
    assert len(sync) == 1
    assert type(sync[0]) is Conflict
    con = ConflictResolverFile(sync[0], sync_core)
    con.resolve(None)
    assert are_dir_trees_equal(TEST_DIR_A, TEST_DIR_B) is True


def copy_add_add_dir_without_conflicts():
    copy_a_and_b()
    sync_core = SyncCore(TEST_DIR_A, TEST_DIR_B)

    create_struct({
        "new_dir": {
            "dir": {
                "test.txt": "new world"
            },
            "file.txt": "hello"
        }
    }, os.path.join(TEST_DIR_A, "a", "b"))
    create_struct({
        "new_dir": {
            "dir": {
                "test2.txt": "new world"
            },
            "file2.txt": "hello"
        }
    }, os.path.join(TEST_DIR_B, "a", "b"))
    sync = sync_core.sync_dir()
    assert len(sync) == 0
    assert are_dir_trees_equal(TEST_DIR_A, TEST_DIR_B) is True


def copy_add_add_dir_conflicts():
    copy_a_and_b()
    sync_core = SyncCore(TEST_DIR_A, TEST_DIR_B)

    create_struct({
        "new_dir": {
            "dir": {
                "test.txt": "new world"
            },
            "file.txt": "hello"
        }
    }, os.path.join(TEST_DIR_A, "a", "b"))
    create_struct({
        "new_dir": {
            "dir": {
                "test.txt": "new world2"
            },
            "file2.txt": "hello"
        }
    }, os.path.join(TEST_DIR_B, "a", "b"))
    sync = sync_core.sync_dir()
    assert len(sync) == 1
    assert type(sync[0]) is Conflict
    assert os.path.normpath(sync[0].path1) == \
           os.path.normpath(os.path.join(TEST_DIR_A, "a", "b",
                                         "new_dir", "dir", "test.txt"))
    con = ConflictResolverFile(sync[0], sync_core)
    con.resolve("zaq1")
    assert are_dir_trees_equal(TEST_DIR_A, TEST_DIR_B) is True


def copy_remove_remove_dir_without_conflicts():
    copy_a_and_b()
    sync_core = SyncCore(TEST_DIR_A, TEST_DIR_B)

    shutil.rmtree(
        os.path.join(TEST_DIR_A, "a/b"))
    shutil.rmtree(
        os.path.join(TEST_DIR_B, "a/b"))
    sync = sync_core.sync_dir()
    assert len(sync) == 0
    assert are_dir_trees_equal(TEST_DIR_A, TEST_DIR_B) is True


if __name__ == "__main__":
    copy_a2b()
    copy_b2a()
    copy_a_and_b()
    copy_add_add_file()
    copy_remove_remove_file()
    copy_remove_edit_file_remove()
    copy_remove_edit_file_delete()
    copy_edit_remove_file_remove()
    copy_edit_remove_file_delete()
    copy_edit_edit_file()
    copy_add_add_dir_without_conflicts()
    copy_add_add_dir_conflicts()
    copy_remove_remove_dir_without_conflicts()
