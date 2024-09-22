import json
from base64 import b64decode, b64encode
from datetime import datetime
from hashlib import sha3_256
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    BLOB,
    CHAR,
    JSON,
    TIMESTAMP,
    Boolean,
    CheckConstraint,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from program_env import program_env
from store.dbase import Base
from util.hashing import hash_digest
from util.json_utils import json_dumps

is_global = True if program_env.is_production else None


class DParameters(Base):
    __tablename__ = "parameters"
    """Metadata to group many 'runs' with a 'master_seed' and configuration"""

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, insert_default=uuid4)

    seed: Mapped[UUID] = mapped_column(nullable=False)
    parameters: Mapped[object] = mapped_column(JSON(), nullable=False)
    hash: Mapped[str] = mapped_column(CHAR(length=44), nullable=False)
    """The hash of the seed & parameter."""

    is_global: Mapped[Optional[bool]] = mapped_column(
        Boolean(), insert_default=lambda: is_global
    )
    """If true, no repeats is enforced."""

    start_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(), nullable=False, insert_default=func.now()
    )

    @declared_attr.directive
    def __table_args__(cls) -> tuple:
        # Null is allowed, but False is disallowed
        # TODO check that this works by inserting False
        return (
            UniqueConstraint(cls.hash, cls.is_global),
            CheckConstraint(cls.is_global != False),
        )

    def __init__(self, seed: UUID, parameters: object):
        self.seed = seed
        self.parameters = parameters
        parameters_json = bytes(json_dumps(parameters), "ascii")

        digest = hash_digest(seed.bytes, parameters_json)
        self.hash = b64encode(digest).decode("ascii")
