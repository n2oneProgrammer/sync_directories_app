import json
import os
import unittest
from unittest.mock import mock_open, Mock, MagicMock, patch
from units_tests.directory_simulator.directory_simulator import DirectorySimulator
from utilities.sync_core_libs.diff_type import DiffType
from utilities.sync_core_libs.status_sync_file import StatusSyncFile
from utilities.sync_core_libs.sync_core import SyncCore

from utilities.hash import Hash


@patch("utilities.hash.Hash.md5")
class SyncCoreGenerateStructureTest(unittest.TestCase):

    def setUp(self):
        self.directory_simulator = DirectorySimulator()
        self.directory_simulator.directory_structure = {
            "C:": {
                "a": {
                    "b": {
                        "c.txt": "test1",
                        "b.txt": "zaq1"
                    },
                    "d.py": "python file"
                },
                "b": {
                    "b": {
                        "c.txt": "test1",
                        "b.txt": "zaq1"
                    },
                    "d.py": "python file"
                }
            }

        }
        self.sync_file = {
            "b": {
                "b\\c.txt": "5a105e8b9d40e1329780d62ea2265d8a",
                "b\\b.txt": "62f2596b743b732c244ca5451a334b4f"
            },
            "d.py": "7fe39e2e3d0444251fe73cd8af113758"
        }
        SyncCore.make_diff = Mock()
        self.sync_core = SyncCore("C:/a", "C:/b")
        self.sync_core.sync_file = self.sync_file
        # mocking
        os.listdir = Mock()
        os.listdir.side_effect = self.directory_simulator.list_dir

        os.path.isdir = Mock()
        os.path.isdir.side_effect = self.directory_simulator.is_dir

        os.path.exists = Mock()
        os.path.exists.side_effect = self.directory_simulator.exist

    def test_without_difference_directories(self, md5_mock):
        md5_mock.side_effect = self.directory_simulator.md5

        self.sync_core.generate_structure("C:/a", "C:/b")
        self.assertEqual(len(self.sync_core.diff_list), 0)

    def test_create_file_in_dir_A(self, md5_mock):
        md5_mock.side_effect = self.directory_simulator.md5
        self.directory_simulator.create_file("C:/a/b/new_file.txt", "NEW FILE")

        self.sync_core.generate_structure("C:/a", "C:/b")

        self.assertEqual(len(self.sync_core.diff_list), 1)
        diff_obj = self.sync_core.diff_list[0]
        self.assertEqual(diff_obj.type, DiffType.Create)
        self.assertEqual(os.path.normpath(diff_obj.src1), os.path.normpath("C:/a/b/new_file.txt"))
        self.assertEqual(os.path.normpath(diff_obj.src2), os.path.normpath("C:/b/b/new_file.txt"))
        self.assertEqual(diff_obj.status, StatusSyncFile.finalCompare)

    def test_create_file_in_dir_B(self, md5_mock):
        md5_mock.side_effect = self.directory_simulator.md5
        self.directory_simulator.create_file("C:/b/b/new_file.txt", "NEW FILE")

        self.sync_core.generate_structure("C:/a", "C:/b")

        self.assertEqual(len(self.sync_core.diff_list), 1)
        diff_obj = self.sync_core.diff_list[0]
        self.assertEqual(diff_obj.type, DiffType.Create)
        self.assertEqual(os.path.normpath(diff_obj.src1), os.path.normpath("C:/b/b/new_file.txt"))
        self.assertEqual(os.path.normpath(diff_obj.src2), os.path.normpath("C:/a/b/new_file.txt"))
        self.assertEqual(diff_obj.status, StatusSyncFile.finalCompare)

    def test_create_file_both(self, md5_mock):
        md5_mock.side_effect = self.directory_simulator.md5
        self.directory_simulator.create_file("C:/a/b/new_file.txt", "NEW FILE 1")
        self.directory_simulator.create_file("C:/b/b/new_file.txt", "NEW FILE 2")

        self.sync_core.generate_structure("C:/a", "C:/b")

        self.assertEqual(len(self.sync_core.diff_list), 1)
        diff_obj = self.sync_core.diff_list[0]
        self.assertEqual(diff_obj.type, DiffType.AddAddConflict)
        self.assertEqual(os.path.normpath(diff_obj.src1), os.path.normpath("C:/a/b/new_file.txt"))
        self.assertEqual(os.path.normpath(diff_obj.src2), os.path.normpath("C:/b/b/new_file.txt"))
        self.assertEqual(diff_obj.status, StatusSyncFile.finalCompare)

    def test_edit_file_in_dir_a(self, md5_mock):
        md5_mock.side_effect = self.directory_simulator.md5
        self.directory_simulator.edit_file("C:/a/d.py", "EDIT FILE")

        self.sync_core.generate_structure("C:/a", "C:/b")

        self.assertEqual(len(self.sync_core.diff_list), 1)
        diff_obj = self.sync_core.diff_list[0]
        self.assertEqual(diff_obj.type, DiffType.Edit)
        self.assertEqual(os.path.normpath(diff_obj.src1), os.path.normpath("C:/a/d.py"))
        self.assertEqual(os.path.normpath(diff_obj.src2), os.path.normpath("C:/b/d.py"))
        self.assertEqual(diff_obj.status, StatusSyncFile.finalCompare)

    def test_edit_file_in_dir_b(self, md5_mock):
        md5_mock.side_effect = self.directory_simulator.md5
        self.directory_simulator.edit_file("C:/b/d.py", "EDIT FILE")

        self.sync_core.generate_structure("C:/a", "C:/b")

        self.assertEqual(len(self.sync_core.diff_list), 1)
        diff_obj = self.sync_core.diff_list[0]
        self.assertEqual(diff_obj.type, DiffType.Edit)
        self.assertEqual(os.path.normpath(diff_obj.src1), os.path.normpath("C:/b/d.py"))
        self.assertEqual(os.path.normpath(diff_obj.src2), os.path.normpath("C:/a/d.py"))
        self.assertEqual(diff_obj.status, StatusSyncFile.finalCompare)

    def test_edit_file_in_both(self, md5_mock):
        md5_mock.side_effect = self.directory_simulator.md5
        self.directory_simulator.edit_file("C:/a/d.py", "EDIT FILE 1")
        self.directory_simulator.edit_file("C:/b/d.py", "EDIT FILE 2")

        self.sync_core.generate_structure("C:/a", "C:/b")

        self.assertEqual(len(self.sync_core.diff_list), 1)
        diff_obj = self.sync_core.diff_list[0]
        self.assertEqual(diff_obj.type, DiffType.EditEditConflict)
        self.assertEqual(os.path.normpath(diff_obj.src1), os.path.normpath("C:/a/d.py"))
        self.assertEqual(os.path.normpath(diff_obj.src2), os.path.normpath("C:/b/d.py"))
        self.assertEqual(diff_obj.status, StatusSyncFile.finalCompare)

    def test_delete_file_in_dir_a(self, md5_mock):
        md5_mock.side_effect = self.directory_simulator.md5
        self.directory_simulator.delete_file("C:/a/d.py")

        self.sync_core.generate_structure("C:/a", "C:/b")

        self.assertEqual(len(self.sync_core.diff_list), 1)
        diff_obj = self.sync_core.diff_list[0]
        self.assertEqual(diff_obj.type, DiffType.Delete)
        self.assertEqual(os.path.normpath(diff_obj.src1), os.path.normpath("C:/a/d.py"))
        self.assertEqual(os.path.normpath(diff_obj.src2), os.path.normpath("C:/b/d.py"))
        self.assertEqual(diff_obj.status, StatusSyncFile.finalCompare)

    def test_delete_file_in_dir_b(self, md5_mock):
        md5_mock.side_effect = self.directory_simulator.md5
        self.directory_simulator.delete_file("C:/b/d.py")

        self.sync_core.generate_structure("C:/a", "C:/b")

        self.assertEqual(len(self.sync_core.diff_list), 1)
        diff_obj = self.sync_core.diff_list[0]
        self.assertEqual(diff_obj.type, DiffType.Delete)
        self.assertEqual(os.path.normpath(diff_obj.src1), os.path.normpath("C:/b/d.py"))
        self.assertEqual(os.path.normpath(diff_obj.src2), os.path.normpath("C:/a/d.py"))
        self.assertEqual(diff_obj.status, StatusSyncFile.finalCompare)

    def test_delete_file_in_both(self, md5_mock):
        md5_mock.side_effect = self.directory_simulator.md5
        self.directory_simulator.delete_file("C:/a/d.py")
        self.directory_simulator.delete_file("C:/b/d.py")

        self.sync_core.generate_structure("C:/a", "C:/b")

        self.assertEqual(len(self.sync_core.diff_list), 1)
        diff_obj = self.sync_core.diff_list[0]
        self.assertEqual(diff_obj.type, DiffType.RemoveRemove)
        self.assertEqual(os.path.normpath(diff_obj.src1), os.path.normpath("C:/a/d.py"))
        self.assertEqual(os.path.normpath(diff_obj.src2), os.path.normpath("C:/b/d.py"))
        self.assertEqual(diff_obj.status, StatusSyncFile.finalCompare)

    def test_delete_file_in_dir_a_and_edit_in_dir_b(self, md5_mock):
        md5_mock.side_effect = self.directory_simulator.md5
        self.directory_simulator.delete_file("C:/a/d.py")
        self.directory_simulator.edit_file("C:/b/d.py", "new value")

        self.sync_core.generate_structure("C:/a", "C:/b")

        self.assertEqual(len(self.sync_core.diff_list), 1)
        diff_obj = self.sync_core.diff_list[0]
        self.assertEqual(diff_obj.type, DiffType.RemoveEditConflict)
        self.assertEqual(os.path.normpath(diff_obj.src1), os.path.normpath("C:/a/d.py"))
        self.assertEqual(os.path.normpath(diff_obj.src2), os.path.normpath("C:/b/d.py"))
        self.assertEqual(diff_obj.status, StatusSyncFile.finalCompare)

    def test_delete_file_in_dir_b_and_edit_in_dir_a(self, md5_mock):
        md5_mock.side_effect = self.directory_simulator.md5
        self.directory_simulator.edit_file("C:/a/d.py", "new value")
        self.directory_simulator.delete_file("C:/b/d.py")

        self.sync_core.generate_structure("C:/a", "C:/b")

        self.assertEqual(len(self.sync_core.diff_list), 1)
        diff_obj = self.sync_core.diff_list[0]
        self.assertEqual(diff_obj.type, DiffType.RemoveEditConflict)
        self.assertEqual(os.path.normpath(diff_obj.src1), os.path.normpath("C:/b/d.py"))
        self.assertEqual(os.path.normpath(diff_obj.src2), os.path.normpath("C:/a/d.py"))
        self.assertEqual(diff_obj.status, StatusSyncFile.finalCompare)
