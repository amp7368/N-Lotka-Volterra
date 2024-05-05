import argparse
import json
import os
from enum import StrEnum
from os import path
from types import SimpleNamespace
from typing import List

NLV_Action = StrEnum("simulate", "generate")


class RawNLVArgs:
    config_files: List[str]
    action: NLV_Action
    outdir: List[str] | None
    outprefix: List[str] | None
    trial: int | None
    interactive: bool


class NLVArgs[Config]:
    current_index: int
    configs: List[Config]
    action: NLV_Action
    output: List[str]
    outputsuffix: str
    interactive: bool

    def __init__(self, raw: RawNLVArgs) -> None:
        self.current_index = 0
        self.configs = []
        self.action = raw.action
        self.output = []
        self.interactive = raw.interactive
        if raw.trial == None:
            self.outputsuffix = ""
        else:
            self.outputsuffix = f"-{raw.trial}"

        # Load config(s)
        for config_i, config_file in enumerate(raw.config_files):

            with open(config_file, "r") as file:
                loaded = json.load(file, object_hook=lambda d: SimpleNamespace(**d))
                self.configs.append(loaded)
                self._append_output(config_i, raw)

    def _append_output(self, config_i: int, raw: RawNLVArgs):
        # Verify outdir and outprefix have at least the same length as self.config
        if len(raw.outdir) <= config_i:
            folder, path_ext = path.splitext(raw.config_files[config_i])
            raw.outdir.append(folder)
        if len(raw.outprefix) <= config_i:
            fname = path.basename(raw.outdir[config_i])
            raw.outprefix.append(fname)

        # append final outputdir for this config
        folder = raw.outdir[config_i]
        prefix = raw.outprefix[config_i]
        out = path.join(folder, prefix)
        self.output.append(path.normpath(out))

        # Create out folder
        folder = path.dirname(self.output[config_i])
        if path.isdir(folder):
            return

        try:
            os.makedirs(folder)
        except:
            raise FileExistsError(
                f"Error creating directory: {folder}! Verify that {raw.outprefix[config_i]} has "
                + "an extension, so a folder with  name can be made."
            )

    def config(self):
        return self.configs[self.current_index]

    def output_file(self, f: str, ext: str):
        output = self.output[self.current_index]
        return f"{output}-{f}{self.outputsuffix}.{ext}"


def _normalize_rawargs(raw):
    if not raw.outdir:
        raw.outdir = []
    elif len(raw.outdir) == 1:
        raw.outdir *= len(raw.config_files)
        for i, config in enumerate(raw.config_files):
            subdir, ext = path.splitext(path.basename(config))
            raw.outdir[i] = path.join(raw.outdir[i], subdir)
    if not raw.outprefix:
        raw.outprefix = []
    elif len(raw.outprefix) == 1:
        raw.outprefix *= len(raw.config_files)
    return raw


def parse_args() -> NLVArgs:
    parser = argparse.ArgumentParser(
        prog="N-Lotka Volterra",
        description="Simulate Lotka Volterra models with N species",
    )
    parser.add_argument(
        "--interactive",
        "-ui",
        help="Whether the program should be interactive and stop on plots",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--config-file",
        "-f",
        nargs="+",
        dest="config_files",
        required=True,
        help="The configuration file(s) used as input for the chosen action",
    )
    parser.add_argument(
        "--action",
        "-a",
        default="simulate",
        choices=["simulate", "generate"],
        help="The action to perform",
    )
    parser.add_argument(
        "--outprefix",
        nargs="+",
        help="""Output prefix (defaults to filename of -f).
        Example: -o example --outprefix prefix produces files: [example/prefix-config-[trial].json, example/prefix-edges.csv, example/prefix-foodweb.png, ...]""",
    )
    parser.add_argument(
        "--outdir",
        "-o",
        nargs="+",
        default=["out"],
        help="""Output directory. Note that --outprefix defaults to filename of -f
        Example: -f inp.json -o example/subfolder produces files: [example/subfolder/inp-config-[trial].json, example/subfolder/inp-edges.csv, example/subfolder/inp-foodweb.png, ...]""",
    )
    parser.add_argument(
        "--trial",
        "-t",
        help="The trial of this iteration. Appended to --output prefix",
        type=str,
    )
    args = _normalize_rawargs(parser.parse_args())
    return NLVArgs(args)


def merge_obj(merge_onto: object, merge_from: SimpleNamespace, path=[]):
    for key in merge_from.__dict__:
        from_val = merge_from.__dict__[key]
        if key in merge_onto.__dict__:
            # Merge the values
            onto_val = merge_onto.__dict__[key]
            if hasattr(onto_val, "__dict__") and hasattr(from_val, "__dict__"):
                merge_obj(
                    merge_onto.__dict__[key],
                    merge_from.__dict__[key],
                    path + [str(key)],
                )
            elif not isinstance(from_val, type(onto_val)):
                fullpath = ".".join(path + [str(key)])
                raise Exception(
                    f"Conflict at '{fullpath}'. '{onto_val}' <- '{from_val}'"
                )
            else:
                merge_onto.__dict__[key] = from_val

        else:
            # set the currently empty key
            merge_onto.__dict__[key] = from_val
    return merge_onto
