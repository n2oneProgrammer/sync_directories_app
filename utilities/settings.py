import json

from utilities.path import convert_path, get_storage


class Settings:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.__instance._init()
        return cls.__instance

    def _init(self):
        self.file_name = get_storage() + "/settings.json"

        self.data = {}
        try:
            f = open(self.file_name)
            self.data = json.load(f)
            f.close()
            if self.data == {}:
                raise Exception
        except:
            print("Cannot found " + self.file_name)
            with open(self.file_name, "w") as json_file:
                json.dump({}, json_file)

        self.user_settings = self.set_defaults()

    def set_defaults(self):
        path = convert_path("assets/template/settings.json")
        with open(path) as json_file:
            user_settings = json.load(json_file)
        for item in user_settings:
            if (
                item.get("value") is not None
                and item.get("default") is not None
                and self.get(item["value"]) is None
            ):
                self.set(item["value"], item["default"])
        return user_settings

    def get(self, name):
        return self.data.get(name)

    def set(self, name, value):
        self.data[name] = value
        with open(self.file_name, "w") as json_file:
            json.dump(self.data, json_file)
