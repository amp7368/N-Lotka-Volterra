from abc import ABC, abstractmethod
from os import path, makedirs
from typing import override

from sqlalchemy import URL


class ProgramEnvConn(ABC):
    @abstractmethod
    def url(self) -> URL:
        raise Exception("Not implemented!")

    @abstractmethod
    def is_default(self) -> bool:
        raise Exception


class ProgramEnvPostgresConn(ProgramEnvConn):
    username: str
    password: str
    host: str
    port: int
    database: str
    driver: str

    def __init__(self) -> None:
        self.username = ""
        self.password = ""
        self.host = "localhost"
        self.port = 5432
        self.database = "NLotka"
        self.driver = "postgresql"

    @override
    def url(self) -> URL:
        return URL.create(
            self.driver,
            self.username,
            self.password,
            self.host,
            self.port,
            self.database,
        )

    @override
    def is_default(self) -> bool:
        return (
            len(self.username) == 0
            and len(self.password) == 0
            and self.host == "localhost"
            and self.port == 5432
            and self.database == "NLotka"
        )


class ProgramEnvSQLiteConn(ProgramEnvConn):
    filepath: str
    driver: str
    user_verified_configuration: bool

    def __init__(self) -> None:
        self.filepath = "./run/lotka_db.sqlite"
        self.driver = "sqlite+pysqlite"
        self.user_verified_configuration = False

    @override
    def url(self) -> URL:
        dir = path.dirname(self.filepath)
        if not path.exists(dir):
            makedirs(dir)
        return URL.create(self.driver, database=self.filepath)

    @override
    def is_default(self) -> bool:
        return self.user_verified_configuration
