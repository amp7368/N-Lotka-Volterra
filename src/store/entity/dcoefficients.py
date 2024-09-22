from uuid import UUID

from networkx import Graph
from sqlalchemy import Double, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from store.dbase import Base
from store.entity.dspecies_run import DSpeciesRun


class DCoefficients(Base):
    __tablename__ = "coefficents"
    source_id: Mapped[UUID] = mapped_column(ForeignKey(DSpeciesRun.id), nullable=False)
    source: Mapped[DSpeciesRun] = relationship(foreign_keys=source_id)
    target_id: Mapped[UUID] = mapped_column(ForeignKey(DSpeciesRun.id), nullable=False)
    target: Mapped[DSpeciesRun] = relationship(foreign_keys=target_id)
    source_to_target: Mapped[float] = mapped_column(Double(), nullable=False)
    target_to_source: Mapped[float] = mapped_column(Double(), nullable=False)

    def __init__(
        self, source: DSpeciesRun, target: DSpeciesRun, s_to_t: float, t_to_s: float
    ):
        self.source = source
        self.target = target
        self.source_id = source.id
        self.target_id = target.id
        self.source_to_target = s_to_t
        self.target_to_source = t_to_s

    @declared_attr.directive
    def __table_args__(cls):
        return (PrimaryKeyConstraint(cls.source_id, cls.target_id),)
