from utilities.folder import Folder
from utilities.settings import Settings


class Storage:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.__instance._init()
        return cls.__instance

    def _init(self):
        self.syncs = self.load_all()

    def load_all(self):
        syncs = Settings().get("syncs")
        if syncs is None:
            Settings().set("syncs", [])
            syncs = []
        objs = []
        for item in syncs:
            objs.append(Folder(item))
        return objs

    def sync_all(self):
        for sync in self.syncs:
            sync.sync()

    def create(self, dict):
        new_folder = Folder(dict)
        self.syncs.append(new_folder)
        return new_folder

    def remove(self, sync):
        syncs = Settings().get("syncs")
        syncs.remove(sync.to_dict())
        Settings().set("syncs", syncs)
        self.syncs.remove(sync)

    def unsubscribe_new_status(self, func):
        for sync in self.syncs:
            sync.event.new_status -= func

    def unsubscribe_new_detail(self, func):
        for sync in self.syncs:
            sync.event.new_detail -= func

    def unsubscribe_all(self):
        for sync in self.syncs:
            sync.create_event()
