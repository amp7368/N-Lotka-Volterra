MAX_SEED_BYTES = 64


class SimulationSeriesId:
    epoch: int
    iteration: int

    def __init__(self, epoch: int, iteration: int) -> None:
        self.epoch = epoch
        self.iteration = iteration

    def to_bytes_list(self):
        epoch_bytes = self.epoch.to_bytes(MAX_SEED_BYTES, "big")
        iteration_bytes = self.iteration.to_bytes(MAX_SEED_BYTES, "big")
        return [epoch_bytes, iteration_bytes]
