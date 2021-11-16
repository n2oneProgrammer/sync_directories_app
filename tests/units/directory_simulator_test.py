import unittest

from directory_simulator.directory_simulator import DirectorySimulator


class DirectorySimulatorCommonMethodTest(unittest.TestCase):

    def setUp(self):
        self.directory_simulator = DirectorySimulator()
        self.directory_simulator.directory_structure = {
            "C:": {
                "a": {
                    "b": {
                        "c": {
                            "d.txt": "test",
                            "binary.txt": bytes("test", "utf-8")
                        },
                        "d": {
                            "d.txt": "test"
                        }
                    }
                }
            }
        }

    def test_is_dir_true(self):
        self.assertTrue(self.directory_simulator.is_dir("C:/a/b"))

    def test_is_dir_false(self):
        self.assertFalse(self.directory_simulator.is_dir("C:/a/b/c/d.txt"))

    def test_is_dir_not_exist(self):
        self.assertFalse(self.directory_simulator.is_dir("C:/a/bx/c/d.txt"))

    def test_exist_true(self):
        self.assertTrue(self.directory_simulator.exist("C:/a/b"))

    def test_exist_false(self):
        self.assertFalse(self.directory_simulator.is_dir("C:/a/z"))

    def test_md5_text(self):
        self.assertEqual(self.directory_simulator.md5("C:/a/b/c/d.txt"), "098f6bcd4621d373cade4e832627b4f6")

    def test_md5_binary(self):
        self.assertEqual(self.directory_simulator.md5("C:/a/b/c/binary.txt"), "098f6bcd4621d373cade4e832627b4f6")

    def test_md5_not_exist_file(self):
        self.assertEqual(self.directory_simulator.md5("C:/a/b/not_exist.py"), None)


class DirectorySimulatorCreateTest(unittest.TestCase):

    def setUp(self):
        self.directory_simulator = DirectorySimulator()

    def test_create_file_without_starts_dirs(self):
        self.directory_simulator.create_file("C:/a/b/c/d.txt", "tests")

        result = {
            "C:": {
                "a": {
                    "b": {
                        "c": {
                            "d.txt": "tests"
                        }
                    }
                }
            }
        }
        self.assertEqual(self.directory_simulator.directory_structure, result)

    def test_create_file_with_starts_dirs(self):
        self.directory_simulator.directory_structure = {
            "C:": {
                "a": {
                    "b": {
                    },
                    "c": {
                        "tests.txt": "test1"
                    }
                }
            }
        }

        self.directory_simulator.create_file("C:/a/b/c/d.txt", "tests")

        result = {
            "C:": {
                "a": {
                    "b": {
                        "c": {
                            "d.txt": "tests"
                        }
                    },
                    "c": {
                        "tests.txt": "test1"
                    }
                }
            }
        }
        self.assertEqual(self.directory_simulator.directory_structure, result)

    def test_create_dirs_without_starts_dirs(self):
        self.directory_simulator.create_dir("C:/a/b/c/d")

        result = {
            "C:": {
                "a": {
                    "b": {
                        "c": {
                            "d": {}
                        }
                    }
                }
            }
        }
        self.assertEqual(self.directory_simulator.directory_structure, result)

    def test_create_dirs_with_starts_dirs(self):
        self.directory_simulator.directory_structure = {
            "C:": {
                "a": {
                    "b": {
                    },
                    "c": {
                        "tests.txt": "test1"
                    }
                }
            }
        }

        self.directory_simulator.create_dir("C:/a/b/c/d")

        result = {
            "C:": {
                "a": {
                    "b": {
                        "c": {
                            "d": {}
                        }
                    },
                    "c": {
                        "tests.txt": "test1"
                    }
                }
            }
        }
        self.assertEqual(self.directory_simulator.directory_structure, result)

    def test_edit_file_with_starts_dirs(self):
        self.directory_simulator.directory_structure = {
            "C:": {
                "a": {
                    "b": {
                    },
                    "c": {
                        "tests.txt": "test1"
                    }
                }
            }
        }

        self.directory_simulator.edit_file("C:/a/c/tests.txt", "new value")

        result = {
            "C:": {
                "a": {
                    "b": {
                    },
                    "c": {
                        "tests.txt": "new value"
                    }
                }
            }
        }
        self.assertEqual(self.directory_simulator.directory_structure, result)

    def test_delete_file_with_starts_dirs(self):
        self.directory_simulator.directory_structure = {
            "C:": {
                "a": {
                    "b": {
                    },
                    "c": {
                        "tests.txt": "test1"
                    }
                }
            }
        }

        self.directory_simulator.delete_file("C:/a/c/tests.txt")

        result = {
            "C:": {
                "a": {
                    "b": {
                    },
                    "c": {
                    }
                }
            }
        }
        self.assertEqual(self.directory_simulator.directory_structure, result)


class DirectorySimulatorListTest(unittest.TestCase):

    def setUp(self):
        self.directory_simulator = DirectorySimulator()
        self.directory_simulator.directory_structure = {
            "C:": {
                "a": {
                    "b": {
                        "c": {
                            "d.txt": "tests"
                        },
                        "d": {
                            "d.txt": "tests"
                        }
                    }
                }
            }
        }

    def test_list_dir(self):
        list = self.directory_simulator.list_dir("C:/a/b")
        result = ["c", "d"]
        self.assertEqual(list, result)

    def test_list_not_exist_dir(self):
        self.assertRaises(FileNotFoundError, self.directory_simulator.list_dir, "C:/a/b/e")

    def test_list_file(self):
        self.assertRaises(NotADirectoryError, self.directory_simulator.list_dir, "C:/a/b/c/d.txt")
