from argparse import ArgumentParser, _SubParsersAction

from args.base_command import parse_base_args
from args.subcommand.generate_command import parse_generate_args
from args.subcommand.simulate_command import parse_simulate_args


def main():
    parser = ArgumentParser(
        prog="N-Lotka Volterra",
        description="Simulate Lotka Volterra models with N species",
    )
    subparsers: _SubParsersAction[ArgumentParser] = parser.add_subparsers(required=True)

    simulate_parser: ArgumentParser = subparsers.add_parser(
        name="simulate",
        description="Run a N-Lotka-Volterra simulation",
    )
    parse_base_args(simulate_parser)
    parse_simulate_args(simulate_parser)

    generate_parser: ArgumentParser = subparsers.add_parser(
        name="generate",
        description="Generate a random model N-Lotka-Volterra simulation",
    )
    parse_generate_args(generate_parser)
    parse_base_args(generate_parser)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
