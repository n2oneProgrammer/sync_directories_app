import unittest
from unittest.mock import Mock

from utilities.sync_core_libs.ignore_file import IgnoreFile


class IgnoreFileTest(unittest.TestCase):
    def test_simple_check_name_true(self):
        IgnoreFile.load_file = Mock()
        IgnoreFile().ignore_file = ["file1.png", "file2.txt", "file3.py"]
        self.assertTrue(IgnoreFile().is_detect("C:/a/b/c", "file3.py"))

    def test_simple_check_name_false(self):
        IgnoreFile.load_file = Mock()
        IgnoreFile().ignore_file = ["file1.png", "file2.txt", "file3.py"]
        self.assertFalse(IgnoreFile().is_detect("C:/a/b/c", "file4.py"))
