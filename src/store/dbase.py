from sqlalchemy import Connection, Engine
from sqlalchemy.orm import DeclarativeBase, Session


class DB:
    engine: Engine

    def connect(self) -> Connection:
        return self.engine.connect()

    def sess(self) -> Session:
        return Session(self.engine)

    def save(self, obj: object) -> None:
        with self.sess() as sess:
            sess.add(obj)
            sess.commit()


db = DB()


class Base(DeclarativeBase):
    pass
