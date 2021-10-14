import hashlib


def md5(fname, limit_MB=200):
    hash_md5 = hashlib.md5()
    count = (limit_MB * 1024) // 4
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
            count = count - 1
            if count == 0:
                break
    return hash_md5.hexdigest()
