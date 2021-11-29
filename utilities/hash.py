import hashlib

from utilities.settings import Settings


class Hash:
    def md5(fname: str, limit_MB=None):
        hash_md5 = hashlib.md5()
        if limit_MB is None:
            limit_MB = Settings().get("limit_hashing_file_MB")
        
        count = (limit_MB * 1024) // 4
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
                count = count - 1
                if count == 0:
                    break
        return hash_md5.hexdigest()
