import json
import sys
from os import cpu_count, path
from types import SimpleNamespace
from typing import List, Optional, override
from uuid import UUID, uuid4

from env.db_connection import (
    ProgramEnvConn,
    ProgramEnvPostgresConn,
    ProgramEnvSQLiteConn,
)
from model.simulation_series_id import SimulationSeriesId
from util.json_utils import ConfigInit, merge_obj, write_file


class ProgramEnvRun(ConfigInit):
    last_seed_used: List[str]
    """Convienience field for the user to see the last N seeds used"""

    master_seed: Optional[str]
    series_id: List[SimulationSeriesId] | Optional[SimulationSeriesId]
    thread_count: int

    def __init__(self) -> None:
        self.last_seed_used = []
        self.master_seed = None
        self.series_id = None
        self.thread_count = 1

    def get_thread_count(self) -> int:
        if self.thread_count > 0:
            return self.thread_count
        return cpu_count()

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
    connections: dict[str, ProgramEnvConn]
    active_connection: str
    CONFIRM_DROP_DATABASE_ONCE: bool
    is_production: bool
    run: ProgramEnvRun

    def __init__(self) -> None:
        self.connections = {
            "postgres": ProgramEnvPostgresConn(),
            "sqlite": ProgramEnvSQLiteConn(),
        }
        self.active_connection = "sqlite"
        self.run = ProgramEnvRun()
        self.is_production = True
        self.CONFIRM_DROP_DATABASE_ONCE = False

    def before_save_hook(self) -> None:
        self.CONFIRM_DROP_DATABASE_ONCE = False

    def database_conn(self) -> ProgramEnvConn:
        active = self.active_connection
        if active not in self.connections:
            listed = [f"'{conn}'" for conn in self.connections.keys()]
            listed = ", ".join(listed)
            print(
                f"'{active}' is not one of the available connections. Please configure {program_env_file}.active_connection to one of the keys in {program_env_file}.connections. Currently, the listed connections are: {listed}"
            )
            sys.exit(1)
        return self.connections[active]

    def save(self) -> None:
        self.before_save_hook()
        write_file(self, program_env_file)


def _load_config():
    if not path.exists(program_env_file):
        write_file(ProgramEnv(), program_env_file)
        print(f"Please configure recently created config file: {program_env_file}.")
        sys.exit(1)

    with open(program_env_file, "r") as file:
        try:
            file_json = json.load(file, object_hook=lambda d: SimpleNamespace(**d))
        except json.JSONDecodeError:
            print(
                f"Please correctly format {file.name}. Or delete the file to regenerate"
            )
            sys.exit(1)
    config: ProgramEnv = merge_obj(ProgramEnv(), file_json)

    # Save a copy of config with 'before_save_hook()' being called.
    # This is so program_env will still have 'CONFIRM_DROP_DATABASE_ONCE' as potentially True
    # so that the initialization can follow the drop database procedure before it's reverted
    merge_obj(ProgramEnv(), file_json).save()

    if config.database_conn().is_default():
        print(f"Please configure {file.name}. The databaseConnection is incomplete")
        sys.exit(1)
    return config


program_env_file: str = path.relpath("ProgramEnv.json")
program_env: ProgramEnv = _load_config()
