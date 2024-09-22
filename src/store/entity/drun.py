from base64 import b64encode
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CHAR,
    JSON,
    TIMESTAMP,
    ForeignKey,
    SmallInteger,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from model.simulation_trial import SimulationTrial
from store.dbase import Base
from store.entity.dparameters import DParameters
from util.hashing import hash_digest, hash_digest_json
from util.json_utils import json_dumps


def generate_run_id():
    id = bytearray(uuid4().bytes)
    id[-1] = 0
    id[-2] = 0
    return UUID(bytes=bytes(id), version=4)


class DRun(Base):
    __tablename__ = "trial_run"
    id: Mapped[UUID] = mapped_column(
        Uuid(), primary_key=True, insert_default=generate_run_id
    )
    configuration_id: Mapped[UUID] = mapped_column(ForeignKey(DParameters.id))
    configuration: Mapped[DParameters] = relationship(foreign_keys=configuration_id)
    trial_index: Mapped[int] = mapped_column(SmallInteger(), nullable=False)
    series_id: Mapped[object] = mapped_column(JSON(), nullable=False)
    series_hash: Mapped[str] = mapped_column(CHAR(length=44), nullable=False)

    run_meta: Mapped[object] = mapped_column(JSON(), nullable=False)
    run_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(), nullable=False, default=func.now()
    )

    def __init__(self, trial: SimulationTrial, configuration: DParameters):
        self.configuration_id = configuration.id
        self.configuration = configuration
        self.trial_index = trial.index
        self.series_id = trial.series_id
        self.series_hash = hash_digest_json(trial.series_id)
        self.run_meta = {
            "accuracy": trial.accuracy,
            "settings": trial.settings,
        }

    @declared_attr.directive
    def __table_args__(cls):
        return (
            UniqueConstraint(cls.configuration_id, cls.series_hash, cls.trial_index),
        )
