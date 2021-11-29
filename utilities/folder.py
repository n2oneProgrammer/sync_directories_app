import uuid
from os import path
from threading import Thread

from events import Events
from kivy.logger import Logger

from utilities.conflict_resolver.conflict_resolver_file import \
    ConflictResolverFile
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

        self.create_event()

        self.sync_core = None
        self.conflicts = []
        self.in_sync = False
        self.error = False
        self.resolving = False
        self.break_sync = False
        self.detail = ""

        self.save()
        self.sync()

    def create_event(self):
        try:
            del self.event
        except:
            pass
        self.event = Events(("new_status", "new_detail"))

    def sync(self):
        Thread(target=self._sync, name=f"Sync {self.name}").start()

    def stop(self):
        self.break_sync = True
        self.event.new_detail()

    def _sync(self):
        if self.in_sync or not self.valid() or self.resolving:
            self.event.new_status()
            return
        self.in_sync = True
        self.error = False
        self.event.new_status()

        Logger.info(f"Sync {self.name}: Starting sync...")
        self.conflicts = []
        self.detail = "Looking for differences..."
        self.event.new_detail()

        try:
            self.sync_core = SyncCore(self.dir1, self.dir2)
        except Exception as e:
            self._set_error(e)
            return

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
                try:
                    self.sync_core.merge_with_out_conflict(item)
                except Exception as e:
                    self._set_error(e)
                    return
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
        Logger.info(f"Sync {self.name}: Sync done.")

    def _set_error(self, error):
        Logger.error(f"Sync {self.name}: {error}")
        self.detail = f"Error: {error}"
        self.error = True
        self.break_sync = False
        self.in_sync = False
        self.event.new_status()
        self.event.new_detail()

    def resolve(self, confilct):
        self.conflicts.remove(confilct)

    def resolve_all(self, which):
        Thread(
            target=self._resolve_all, name=f"Resolving {self.name}", args=(which,)
        ).start()

    def _resolve_all(self, which):
        Logger.info(f"Sync {self.name}: Starting resolving...")
        self.resolving = True
        self.break_sync = False
        self.detail = f"Starting resolving..."
        self.event.new_status()
        self.event.new_detail()

        for conflict in self.conflicts.copy():
            if self.break_sync:
                self.break_sync = False
                self.resolving = False
                self.detail = "Resolving stopped."
                self.event.new_status()
                self.event.new_detail()
                return

            resolver = ConflictResolverFile(conflict, self.sync_core)
            if which == 1:
                content = resolver.get_content_path1()
            else:
                content = resolver.get_content_path2()
            content.text = content.get_content()

            e = resolver.resolve(content)
            if e is None:
                self.resolve(conflict)
            else:
                self.conflicts[self.conflicts.index(conflict)].set_error(e)

            self.detail = f"Resolving {conflict.path1}"
            self.event.new_detail()

        self.resolving = False
        self.detail = "Resolving done."
        self.event.new_status()
        self.event.new_detail()
        Logger.info(f"Sync {self.name}: Resolving done.")

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
        if not self.valid():
            return "folder-alert"
        if self.in_sync:
            return "sync"
        if self.resolving:
            return "wrench"
        if len(self.conflicts) > 0:
            return "sync-alert"
        if self.error:
            return "alert"
        return "check"

    def valid(self):
        return path.exists(self.dir1) and path.exists(self.dir2)
