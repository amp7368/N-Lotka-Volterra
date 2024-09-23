from random import Random
from typing import List
from uuid import UUID

from util.hashing import hash_digest


class Seed:
    uuid: UUID
    random: Random

    def __init__(self, seed: UUID) -> None:
        self.uuid = seed
        self.random = Random(seed.bytes)

    def generate_random(self, first_bytes: bytes, *all_bytes: List[bytes]) -> Random:
        initial_seed_bytes = self.uuid.bytes

        digest = hash_digest(initial_seed_bytes, first_bytes, *all_bytes)

        seed = Random(digest).randbytes(16)
        return Random(seed)
