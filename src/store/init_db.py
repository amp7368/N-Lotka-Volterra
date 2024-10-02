import sys

from sqlalchemy import create_engine

from env.program_env import program_env, program_env_file
from store.dbase import Base, db
from util.json_utils import json_dumps


def connect_database():
    db.engine = create_engine(
        program_env.database_conn().url(),
        json_serializer=json_dumps,
    )
    from store.entity import (
        danalysis_cname,
        danalysis_datapoint,
        dcoefficients,
        dparameters,
        drun,
        dspecies_run,
    )


def confirm_delete_db():
    user_input = input(
        "ARE YOU INTENDING TO DROP THE DATABASE?\n"
        + "Input 'y' or 'Y' to confirm yes. Anything other response or program termination will cancel the drop.\n"
        + "... "
    )

    if user_input in ["y", "Y"]:
        # from store.dbase import Base, db

        Base.metadata.drop_all(bind=db.engine)
        print("Recieved confirmation. Database has been dropped! Recreating now.")
    else:
        print("Canceled database drop.")
        print(f"Reset CONFIRM_DROP_DATABASE_ONCE to 'false' in {program_env_file}")
        sys.exit(0)


def init_db():
    connect_database()

    if program_env.CONFIRM_DROP_DATABASE_ONCE:
        confirm_delete_db()
    Base.metadata.create_all(bind=db.engine)
