from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import TEXT, VARCHAR, Uuid, select
from sqlalchemy.orm import Mapped, mapped_column

from store.dbase import Base, db


class DAnalysisColumnName(Base):
    __tablename__ = "analysis_column_name"
    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, insert_default=uuid4)
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(TEXT(), nullable=True)

    def __init__(self, id: Optional[UUID], name: str, description: str) -> None:
        if id is not None:
            self.id = id
        self.name = name
        self.description = description


def __verify_cname(
    q, id: Optional[UUID], name: str, description: str
) -> DAnalysisColumnName:
    with db.sess() as sess:
        cname: DAnalysisColumnName | None = sess.execute(q).one_or_none()
        if cname is not None:
            cname = cname[0]
            if cname.description == description and cname.name == name:
                return cname
            cname.name = name
            cname.description = description
        else:
            cname = DAnalysisColumnName(id, name, description)
        sess.add(cname)
        sess.commit()
        return cname


def get_column(
    name: str, description: Optional[str] = None, id: Optional[UUID] = None
) -> DAnalysisColumnName:
    if id is None:
        q = (
            select(DAnalysisColumnName)
            .where(DAnalysisColumnName.name.ilike(name))
            .limit(1)
        )
    else:
        q = select(DAnalysisColumnName).where(DAnalysisColumnName.id == id)

    return __verify_cname(q, id, name, description)
