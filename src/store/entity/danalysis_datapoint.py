from uuid import UUID

from sqlalchemy import Double, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from store.dbase import Base
from store.entity.danalysis_cname import DAnalysisColumnName
from store.entity.drun import DRun


class DAnalysisDatapoint(Base):
    __tablename__ = "analysis_datapoint"

    cname_id: Mapped[UUID] = mapped_column(
        ForeignKey(DAnalysisColumnName.id), index=True
    )
    cname: Mapped[DAnalysisColumnName] = relationship(foreign_keys=cname_id)
    run_id: Mapped[UUID] = mapped_column(ForeignKey(DRun.id))
    run: Mapped[DRun] = relationship(foreign_keys=run_id)
    value: Mapped[float] = mapped_column(Double())

    def __init__(self, run: DRun, column: DAnalysisColumnName, value: float):
        self.cname = column
        self.run = run
        self.value = value

    @declared_attr.directive
    def __table_args__(cls):
        return (PrimaryKeyConstraint("cname_id", "run_id"),)
