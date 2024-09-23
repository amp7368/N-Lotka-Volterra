from base64 import b64encode
from hashlib import sha3_256
from typing import List

from util.json_utils import json_dumps


def hash_digest(first_bytes: bytes, *all_bytes: List[bytes]) -> bytes:
    hash = sha3_256()
    hash.update(first_bytes)

    for bytes in all_bytes:
        hash.update(bytes)

    return hash.digest()


def hash_digest_json(obj: object) -> str:
    series_json = bytes(json_dumps(obj), "ascii")
    digest = hash_digest(series_json)
    return b64encode(digest).decode("ascii")
