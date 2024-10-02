from io import TextIOWrapper
from os import path, makedirs
from typing import List
from uuid import UUID

from sqlalchemy import distinct, select

from store.entity.danalysis_cname import DAnalysisColumnName
from store.entity.danalysis_datapoint import DAnalysisDatapoint
from store.entity.dparameters import DParameters
from store.entity.drun import DRun
from store.init_db import db, init_db


def export_parameter_runs(sess, parameter_id, file: TextIOWrapper):
    cnames_query = (
        select(DAnalysisColumnName.id, DAnalysisColumnName.name)
        .distinct()
        .join(DAnalysisDatapoint.cname)
        .join(DRun, DRun.id == DAnalysisDatapoint.run_id)
        .where(DRun.parameters_id == parameter_id)
        .order_by(DAnalysisColumnName.name)
    )
    columns: List[tuple[UUID, str]] = sess.execute(cnames_query).all()
    cids = [col[0] for col in columns]
    cnames = [col[1] for col in columns]

    file.write("run_id,")
    file.write(",".join(cnames))
    file.write("\n")

    parameter_runs_query = (
        select(
            DAnalysisDatapoint.cname_id,
            DAnalysisDatapoint.value,
            DAnalysisDatapoint.run_id,
        )
        .join(DRun, DRun.id == DAnalysisDatapoint.run_id)
        .where(DRun.parameters_id == parameter_id)
        .order_by(DRun.id)
    )

    datapoint: dict[UUID, float] = {}
    last_run_id = None
    for col, value, run_id in sess.execute(parameter_runs_query).yield_per(1000):
        if run_id != last_run_id and last_run_id is not None:
            values = [str(datapoint[cid]) for cid in cids]
            file.write(f"'{last_run_id}',")
            file.write(",".join(values))
            file.write("\n")
            datapoint = {}

        last_run_id = run_id
        datapoint[col] = value
    if datapoint:
        file.write(f"'{last_run_id}',")
        values = [str(datapoint[cid]) for cid in cids]
        file.write(",".join(values))
        file.write("\n")


def export():
    init_db()
    include_parameter_ids: List[str] = ["62b95be7-c2ef-4451-8e98-9e5a1266cc7f"]
    folder = "./run/export"
    if not path.exists(folder):
        makedirs(folder)

    if not include_parameter_ids:
        with db.sess() as sess:
            include_parameter_ids = sess.execute(select(DParameters.id)).scalars()
    else:
        include_parameter_ids = [UUID(hex=id) for id in include_parameter_ids]

    with db.sess() as sess:
        for parameter_id in include_parameter_ids:
            with open(path.join(folder, f"{parameter_id}.csv"), "w") as file:
                export_parameter_runs(sess, parameter_id, file)


if __name__ == "__main__":
    export()
