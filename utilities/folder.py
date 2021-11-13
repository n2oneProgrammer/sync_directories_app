import uuid
from os import path
from threading import Thread

from events import Events

from utilities.conflict_resolver.conflict_resolver_file import ConflictResolverFile
from utilities.notification import Notification
from utilities.settings import Settings
from utilities.sync_core_libs.sync_core import SyncCore


class Folder:
    @staticmethod
    def load_all():
        syncs = Settings().get("syncs")
        if syncs is None:
            Settings().set("syncs", [])
            syncs = []
        objs = []
        for item in syncs:
            objs.append(Folder(item))
        return objs

    def __init__(self, data):
        self.name = data["name"]
        self.dir1 = data["dir1"]
        self.dir2 = data["dir2"]

        if data.get("id") is None:
            self.id = uuid.uuid3(uuid.NAMESPACE_X500, self.name).hex
        else:
            self.id = data["id"]

        self.event = Events(("new_status", "new_detail"))

        self.sync_core = None
        self.conflicts = []
        self.in_sync = False
        self.detail = ""
        self.save()

        self.sync()

    def sync(self):
        Thread(target=self._sync, name=f"Sync {self.name}").start()

    def _sync(self):
        if self.in_sync or not self.valid():
            self.event.new_status()
            return
        self.in_sync = True
        self.event.new_status()

        print("Syncing:", self.name)
        self.conflicts = []
        self.detail = "Looking for differences..."
        self.event.new_detail()
        self.sync_core = SyncCore(self.dir1, self.dir2)

        for item in self.sync_core.diff_list.copy():
            c = item.get_conflict()
            if c is None:
                self.detail = (
                    "Removing file..."
                    if item.get_name() is None
                    else f"Coping {item.get_name()}"
                )

                self.event.new_detail()
                self.sync_core.merge_with_out_conflict(item)
            else:
                self.detail = "Conflict found."
                self.event.new_detail()
                self.conflicts.append(c)

        if len(self.conflicts) > 0:
            Notification().notify(
                "Detected confilcts",
                f"In {self.name} found {len(self.conflicts)} conflicts.",
            )

        self.in_sync = False
        self.detail = "Sync done."
        self.event.new_status()
        self.event.new_detail()
        print("DONE")

    def resolve(self, confilct):
        self.conflicts.remove(confilct)

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
        self.force_update()

    def force_update(self):
        if Settings().get("update") == True:
            return
        Settings().set("update", True)

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
