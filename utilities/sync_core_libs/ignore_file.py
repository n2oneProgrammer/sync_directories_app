from utilities.settings import Settings


class IgnoreFile:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.__instance._init()
        return cls.__instance

    def _init(self):
        self.ignore_file_name = Settings().get("Ignore_file_name")
        if self.ignore_file_name is None:
            self.ignore_file_name = ".ignore_sync"

        self.ignore_file = []
        self.load_file()

    def is_detect(self, src, name):
        print(src, name, self.ignore_file)
        for line in self.ignore_file:
            if name == line:
                return True
        return False

    def load_file(self):
        with open(self.ignore_file_name, "r") as file:
            data = file.readlines()
            for line in data:
                self.ignore_file.append(line)
