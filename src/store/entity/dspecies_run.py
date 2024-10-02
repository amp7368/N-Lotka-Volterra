from uuid import UUID

from sqlalchemy import Double, ForeignKey, SmallInteger, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from store.dbase import Base
from store.entity.drun import DRun


class DSpeciesRun(Base):
    __tablename__ = "species_run"
    id: Mapped[Uuid] = mapped_column(Uuid(), primary_key=True)
    species_index: Mapped[SmallInteger] = mapped_column(SmallInteger(), nullable=False)
    run_id: Mapped[Uuid] = mapped_column(
        Uuid, ForeignKey(DRun.id), nullable=False, index=True
    )

    growth_rate: Mapped[Double] = mapped_column(Double(), nullable=False)
    initial_population: Mapped[Double] = mapped_column(Double(), nullable=False)
    days_survived: Mapped[Double] = mapped_column(Double(), nullable=False)

    def __init__(
        self,
        run: DRun,
        species: int,
        growth_rate: float,
        initial_population: float,
        days_survived: int,
    ):
        id = int.from_bytes(run.id.bytes) + species
        self.id = UUID(int=id, version=4)
        self.species_index = species
        self.run_id = run.id
        self.growth_rate = growth_rate
        self.initial_population = initial_population
        self.days_survived = days_survived

    @declared_attr.directive
    def __table_args__(cls):
        return (UniqueConstraint("species_index", "run_id"),)
