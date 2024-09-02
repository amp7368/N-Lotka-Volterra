from argparse import ArgumentParser
from typing import override

from args.base_command import BaseNLVArgs, BaseRawNLVArgs, merge_obj
from model.simulate_options import SimulationOptions


class SimulateRawNLVArgs(BaseRawNLVArgs):
    trial: int | None

    @override
    def outputsuffix(self) -> str:
        parent: str = super().outputsuffix()
        if self.trial == None:
            return parent
        else:
            return f"{parent}-{self.trial}"


class SimulateNLVArgs(BaseNLVArgs[SimulationOptions]):

    @override
    def _generate_config(self, loaded) -> SimulationOptions:
        return merge_obj(SimulationOptions(), loaded)
