import uuid
from os import path
from threading import Thread

from utilities.notification import Notification
from utilities.settings import Settings
from utilities.sync_core import SyncCore


class Folder:
    @staticmethod
    def load_all(callback=lambda: None):
        syncs = Settings().get("syncs")
        if syncs is None:
            Settings().set("syncs", [])
            syncs = []
        objs = []
        for item in syncs:
            objs.append(Folder(item, callback))
        return objs

    def __init__(self, data, callback=lambda: None):
        self.name = data["name"]
        self.dir1 = data["dir1"]
        self.dir2 = data["dir2"]
        if data.get("id") is None:
            self.id = uuid.uuid3(uuid.NAMESPACE_X500, self.name).hex
        else:
            self.id = data["id"]
        self.sync_core = SyncCore(self.dir1, self.dir2)
        self.conflicts = []
        self.in_sync = False
        self.save()

        self.sync(callback)

    def sync(self, callback=lambda: None):
        Thread(target=self._sync, args=(callback,), name=f"Sync {self.name}").start()

    def _sync(self, callback):
        if self.in_sync or not self.valid():
            callback()
            return
        self.in_sync = True
        callback()

        print("Syncing:", self.name, self.in_sync)
        self.conflicts = self.sync_core.sync_dir()

        if len(self.conflicts) > 0:
            Notification().notify(
                "Detected confilcts",
                f"In {self.name} found {len(self.conflicts)} conflicts.",
            )

        self.in_sync = False
        callback()

    def resolve_all(self):
        for item in self.conflicts:
            item.resolve()

    def save(self):
        syncs = Settings().get("syncs")

        ok = True
        for item in syncs:
            if item["id"] == self.id:
                item = self.to_dict()
                ok = False
                break
        if ok:
            syncs.append(self.to_dict())

        Settings().set("syncs", syncs)

    def delete(self):
        syncs = Settings().get("syncs")
        syncs.remove(self.to_dict())
        Settings().set("syncs", syncs)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "dir1": self.dir1, "dir2": self.dir2}

    def status(self):
        if self.in_sync:
            return "sync"
        if not self.valid():
            return "folder-alert"
        if len(self.conflicts) > 0:
            return "sync-alert"
        return "check"

    def valid(self):
        return path.exists(self.dir1) and path.exists(self.dir2)
