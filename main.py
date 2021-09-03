import sys

from sync_core import SyncCore

if __name__ == "__main__":
    dirs = sys.argv[1:3]
    sync = SyncCore(dirs[0], dirs[1])
    sync.sync_dir()
