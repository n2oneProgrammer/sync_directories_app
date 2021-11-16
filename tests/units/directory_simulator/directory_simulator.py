import hashlib
import os
from os.path import normpath, exists


class DirectorySimulator:

    def __init__(self):
        self.directory_structure = {}

    def create_file(self, file_src, content):
        all_dirs = normpath(file_src).split("\\")
        directory = self.directory_structure
        for dir in all_dirs[0:-1]:
            if dir in directory:
                directory = directory[dir]
            else:
                directory[dir] = {}
                directory = directory[dir]
        directory[all_dirs[-1]] = content

    def edit_file(self, file_src, content):
        all_dirs = normpath(file_src).split("\\")
        directory = self.directory_structure
        for dir in all_dirs[0:-1]:
            if dir in directory:
                directory = directory[dir]
            else:
                raise FileNotFoundError("I dont found file " + file_src)
        if all_dirs[-1] not in directory:
            raise FileNotFoundError("I dont found file " + file_src)
        directory[all_dirs[-1]] = content

    def delete_file(self, file_src):
        all_dirs = normpath(file_src).split("\\")
        directory = self.directory_structure
        for dir in all_dirs[0:-1]:
            if dir in directory:
                directory = directory[dir]
            else:
                raise FileNotFoundError("I dont found file " + file_src)
        if all_dirs[-1] not in directory:
            raise FileNotFoundError("I dont found file " + file_src)
        del directory[all_dirs[-1]]

    def create_dir(self, file_src):
        all_dirs = normpath(file_src).split("\\")
        directory = self.directory_structure
        for dir in all_dirs:
            if dir in directory:
                directory = directory[dir]
            else:
                directory[dir] = {}
                directory = directory[dir]

    def find_branch(self, src):
        all_dirs = normpath(src).split("\\")
        directory = self.directory_structure
        for dir in all_dirs:
            if dir in directory:
                directory = directory[dir]
            else:
                return None
        return directory

    def list_dir(self, src):
        found_dir = self.find_branch(src)
        if found_dir is None:
            raise FileNotFoundError("Not found directory " + src)
        if type(found_dir) is str:
            raise NotADirectoryError(src + " is not a directory")

        return list(found_dir.keys())

    def is_dir(self, src):
        all_dirs = normpath(src).split("\\")
        directory = self.directory_structure
        for dir in all_dirs[0:-1]:
            if dir in directory:
                directory = directory[dir]
            else:
                return False

        if all_dirs[-1] not in directory:
            return False

        return type(directory[all_dirs[-1]]) is dict

    def md5(self, parse, limit_MB=200):
        all_dirs = normpath(parse).split("\\")
        directory = self.directory_structure
        for dir in all_dirs[0:-1]:
            if dir in directory:
                directory = directory[dir]
            else:
                return None
        if all_dirs[-1] not in directory:
            return None
        if type(directory[all_dirs[-1]]) is str:
            data = directory[all_dirs[-1]].encode('utf-8')
        else:
            data = directory[all_dirs[-1]][:(limit_MB * 1024)]
        hash_md5 = hashlib.md5(data)
        return hash_md5.hexdigest()

    def exist(self, src):
        all_dirs = normpath(src).split("\\")
        directory = self.directory_structure
        for dir in all_dirs:
            if dir in directory:
                directory = directory[dir]
            else:
                return False
        return True


if __name__ == "__main__":
    dir = DirectorySimulator()
    dir.create_file("a/b/c/z.txt", "asdf")
    dir.create_file("a/b/c/m.txt", "aszxzxxzdf")
    print(dir.directory_structure)
