import json
from os import path
from types import SimpleNamespace
from typing import List, Optional, override
from uuid import UUID, uuid4

from sqlalchemy import URL

from model.simulation_series_id import SimulationSeriesId
from util.json_utils import ConfigInit, merge_obj, write_file


class ProgramEnvConn:
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

    def url(self) -> URL:
        return URL.create(
            self.driver,
            self.username,
            self.password,
            self.host,
            self.port,
            self.database,
        )

    def is_default(self) -> bool:
        return (
            len(self.username) == 0
            and len(self.password) == 0
            and self.host == "localhost"
            and self.port == 5432
            and self.database == "NLotka"
        )


class ProgramEnvRun(ConfigInit):
    last_seed_used: List[str]
    """Convienience field for the user to see the last N seeds used"""

    master_seed: Optional[str]
    series_id: List[SimulationSeriesId] | Optional[SimulationSeriesId]

    def __init__(self) -> None:
        self.last_seed_used = []
        self.master_seed = None
        self.series_id = None

    @override
    def on_config_load(self) -> None:
        if isinstance(self.series_id, list) and not self.series_id:
            self.series_id = None

    def _add_last_seed_used(self, seed: UUID):
        self.last_seed_used.insert(0, seed)
        self.last_seed_used = self.last_seed_used[:5]
        program_env.save()

    def get_or_gen_master_seed(self) -> UUID:
        if self.master_seed is None:
            seed = uuid4()
            print(f"Master Seed of {seed} was randomly generated")
        else:
            seed: UUID = UUID(self.master_seed)
            print(f"Master Seed of {seed} set by user in {program_env_file}")
        self._add_last_seed_used(seed)
        return seed


class ProgramEnv:
    database_conn: ProgramEnvConn
    CONFIRM_DROP_DATABASE_ONCE: bool
    is_production: bool
    run: ProgramEnvRun

    def __init__(self) -> None:
        self.database_conn = ProgramEnvConn()
        self.run = ProgramEnvRun()
        self.is_production = True
        self.CONFIRM_DROP_DATABASE_ONCE = False

    def before_save_hook(self) -> None:
        self.CONFIRM_DROP_DATABASE_ONCE = False

    def save(self) -> None:
        self.before_save_hook()
        write_file(self, program_env_file)


def _load_config():
    if not path.exists(program_env_file):
        write_file(ProgramEnv(), program_env_file)
        print(f"Please configure recently created config file: {program_env_file}.")
        exit(1)

    with open(program_env_file, "r") as file:
        try:
            file_json = json.load(file, object_hook=lambda d: SimpleNamespace(**d))
        except json.JSONDecodeError:
            print(
                f"Please correctly format {file.name}. Or delete the file to regenerate"
            )
            exit(1)
    config: ProgramEnv = merge_obj(ProgramEnv(), file_json)

    # Save a copy of config with 'before_save_hook()' being called.
    # This is so program_env will still have 'CONFIRM_DROP_DATABASE_ONCE' as potentially True
    # so that the initialization can follow the drop database procedure before it's reverted
    merge_obj(ProgramEnv(), file_json).save()

    if config.database_conn.is_default():
        print(f"Please configure {file.name}. The databaseConnection is incomplete")
        exit(1)
    return config


program_env_file: str = path.relpath("ProgramEnv.json")
program_env: ProgramEnv = _load_config()