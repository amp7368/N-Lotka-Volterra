from argparse import ArgumentParser

from args.base_command import merge_obj
from args.subcommand.simulate_args import SimulateNLVArgs, SimulateRawNLVArgs
from model.simulate import run_simulate


def simulate_command(args: SimulateRawNLVArgs):
    args = merge_obj(SimulateRawNLVArgs(), args)
    args.normalize()
    args: SimulateNLVArgs = SimulateNLVArgs(args)

    while args.next():
        simulation = run_simulate(args)


def parse_simulate_args(parser: ArgumentParser):
    parser.add_argument(
        "--trial",
        "-t",
        help="The trial of this iteration. Appended to --output prefix",
        type=str,
    )

    parser.set_defaults(func=simulate_command)
