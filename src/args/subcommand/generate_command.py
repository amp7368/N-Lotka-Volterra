from argparse import ArgumentParser
from typing import override
from args.base_command import BaseNLVArgs, BaseRawNLVArgs, merge_obj
from model.generate import run_generate
from model.generate_options import GenerateOptions


class GenerateRawNLVArgs(BaseRawNLVArgs):
    pass


class GenerateNLVArgs(BaseNLVArgs[GenerateOptions]):

    @override
    def _generate_config(self, loaded) -> GenerateOptions:
        return merge_obj(GenerateOptions(), loaded)


def generate_command(args: GenerateRawNLVArgs):
    args = merge_obj(GenerateRawNLVArgs(), args)
    args.normalize()
    args: GenerateNLVArgs = GenerateNLVArgs(args)

    while args.next():
        simulation = run_generate(args)


def parse_generate_args(parser: ArgumentParser):
    parser.set_defaults(func=generate_command)
