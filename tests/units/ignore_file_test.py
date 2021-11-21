import unittest
from unittest.mock import Mock

from utilities.sync_core_libs.ignore_file import IgnoreFile


class IgnoreFileCheckTest(unittest.TestCase):
    def test_simple_check_name_true(self):
        IgnoreFile.load_file = Mock()
        ignore_file = IgnoreFile("src_dir")
        ignore_file.ignore_file = ["file1.png", "file2.txt", "file3.py"]
        self.assertTrue(ignore_file.is_detect("file3.py"))

    def test_simple_check_name_false(self):
        IgnoreFile.load_file = Mock()
        ignore_file = IgnoreFile("src_dir")
        ignore_file.ignore_file = ["file1.png", "file2.txt", "file3.py"]
        self.assertFalse(ignore_file.is_detect("/file4.py"))

    def test_simple_check_dirs_name_false(self):
        IgnoreFile.load_file = Mock()
        ignore_file = IgnoreFile("src_dir")
        ignore_file.ignore_file = ["file1.png", "file2.txt", "b/file3.py"]
        self.assertTrue(ignore_file.is_detect("b/file3.py"))


