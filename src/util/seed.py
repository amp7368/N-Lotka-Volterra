from hashlib import sha3_256
from random import Random
from typing import List, Self
from uuid import UUID


class Seed:
    uuid: UUID
    random: Random

    def __init__(self, seed: UUID) -> None:
        self.uuid = seed
        self.random = Random(seed.bytes)

    def generate_random(self) -> Random:
        return Random(self.random.randbytes(16))

    def generate_seed(self, first_bytes: bytes, *all_bytes: List[bytes]) -> Self:
        initial_seed_bytes = self.uuid.bytes

        hash = sha3_256()
        hash.update(initial_seed_bytes)
        hash.update(first_bytes)

        for bytes in all_bytes:
            hash.update(bytes)

        seed_bytes = Random(hash.digest()).randbytes(16)
        seed = UUID(bytes=seed_bytes, version=4)
        return Seed(seed)
