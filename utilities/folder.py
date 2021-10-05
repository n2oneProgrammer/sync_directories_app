import uuid

from utilities.settings import Settings
from utilities.sync_core import SyncCore


class Folder:
    @staticmethod
    def load_all():
        syncs = Settings.getInstance().get("syncs")
        if syncs is None:
            Settings.getInstance().set("syncs", [])
            syncs = []
        objs = []
        for item in syncs:
            objs.append(Folder(item))
        return objs

    def __init__(self, data):

        from utilities.sync_core import SyncCore

        self.name = data["name"]
        self.dir1 = data["dir1"]
        self.dir2 = data["dir2"]
        if data.get("id") is None:
            self.id = uuid.uuid3(uuid.NAMESPACE_X500, self.name).hex
        else:
            self.id = data["id"]
        self.sync_core = SyncCore(self.dir1, self.dir2)
        self.conflicts = []
        self.save()

        self.sync()

    def sync(self):
        print("Syncing:", self.name)

        # TODO:
        # This need to be asyc

        a = self.sync_core.sync_dir()

    def resolve_all(self):
        for item in self.conflicts:
            item.resolve()

    def save(self):
        syncs = Settings.getInstance().get("syncs")

        ok = True
        for item in syncs:
            if item["id"] == self.id:
                item = self.to_dict()
                ok = False
                break
        if ok:
            syncs.append(self.to_dict())

        Settings.getInstance().set("syncs", syncs)

    def delete(self):
        syncs = Settings.getInstance().get("syncs")
        syncs.remove(self.to_dict())
        Settings.getInstance().set("syncs", syncs)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "dir1": self.dir1, "dir2": self.dir2}
