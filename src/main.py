import threading
from concurrent.futures import ThreadPoolExecutor
from threading import Event, Lock
from time import time
from traceback import print_exception

from config.load_parameters import load_arguments
from config.parameters_api import ProgramParametersApi
from model.simulation_series_id import SimulationSeriesId
from run_simulation import run_simulation
from store.dbase import db
from store.entity.dparameters import DParameters
from store.init_db import init_db


def ignore(*args):
    pass


threading.excepthook = ignore


class ExecuteEpochs:

    def __init__(self, config: ProgramParametersApi, dparameters: DParameters) -> None:
        self.complete_event = Event()
        self.executor = ThreadPoolExecutor(max_workers=config.epochs.threads)
        self.config = config
        self.dparameters = dparameters
        self.epoch = 0
        self.max_epochs = config.epochs.epochs
        self.iteration = 0
        self.max_iteration = config.epochs.iterations
        self.active_tasks = 0
        self.max_tasks = config.epochs.threads
        self.lock = Lock()

    def locked_increment(self):
        self.iteration += 1
        if self.iteration < self.max_iteration:
            return True
        if self.epoch >= self.max_epochs:
            if self.active_tasks == 0:
                self.complete_event.set()
                self.executor.shutdown()
            return False

        self.iteration = 0
        self.epoch += 1
        return True

    def finish_task(self, ex):
        if ex is not None:
            self.on_exception(ex)

        with self.lock:
            self.active_tasks -= 1
        self.verify_full()

    def run(self, series_id):
        try:
            run_simulation(self.config, self.dparameters, series_id)
        except Exception as e:
            self.finish_task(e)
        else:
            self.finish_task(None)

    def verify_full(self):
        with self.lock:
            while self.active_tasks < self.max_tasks:
                if not self.locked_increment():
                    return
                self.active_tasks += 1

                if self.complete_event.is_set():
                    # Only happens at end of program
                    return
                series_id = SimulationSeriesId(self.epoch, self.iteration)
                self.executor.submit(self.run, series_id)

    def on_exception(self, ex: Exception):
        if isinstance(ex, (SystemExit)):
            self.exit_exception = ex
            self.complete_event.set()
            return
        print_exception(ex)

    def complete(self) -> Exception | None:
        self.verify_full()
        self.complete_event.wait()
        return self.exit_exception


def main():
    init_db()
    start = time()

    config: ProgramParametersApi = load_arguments()
    dparameters: DParameters = DParameters(config.get_master_seed().uuid, config.base)
    db.save(dparameters)

    # No real difference between an epoch and iteration atm
    exit_type: Exception | None = ExecuteEpochs(config, dparameters).complete()

    print(f"Exiting: Ran for {time() - start}s")
    if exit_type is None:
        # Successful exit
        print("Simulations are finished!")
    elif isinstance(exit_type, SystemExit) and exit_type.code == 0:
        print("Program exited normally, but simulations were not run")
    else:
        # Failed exit
        raise exit_type


if __name__ == "__main__":
    main()
