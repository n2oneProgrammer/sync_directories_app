import uuid
from os import path
from threading import Thread

from events import Events

from utilities.notification import Notification
from utilities.settings import Settings
from utilities.sync_core_libs.sync_core import SyncCore


class Folder:
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
        self.break_sync = False
        self.detail = ""

        self.save()
        self.sync()

    def sync(self):
        Thread(target=self._sync, name=f"Sync {self.name}").start()

    def stop(self):
        self.break_sync = True
        self.event.new_detail()

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
            if self.break_sync:
                self.break_sync = False
                self.in_sync = False
                self.detail = "Sync stopped."
                self.event.new_status()
                self.event.new_detail()
                return

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
