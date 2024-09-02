import json
from argparse import ArgumentParser
from os import makedirs, path
from types import SimpleNamespace
from typing import List


class BaseRawNLVArgs:
    config_files: List[str]
    outdir: List[str] | None
    outprefix: List[str] | None
    interactive: bool

    def normalize(self):
        if not self.outdir:
            self.outdir = []
        elif len(self.outdir) == 1:
            self.outdir *= len(self.config_files)
            for i, config in enumerate(self.config_files):
                subdir, ext = path.splitext(path.basename(config))
                self.outdir[i] = path.join(self.outdir[i], subdir)
        if not self.outprefix:
            self.outprefix = []
        elif len(self.outprefix) == 1:
            self.outprefix *= len(self.config_files)
        return self

    def outputsuffix(self) -> str:
        # Might give additional ways to add a suffix later
        return ""


class BaseNLVArgs[Config]:
    current_index: int
    configs: List[Config]
    output: List[str]
    outputsuffix: str
    interactive: bool

    def __init__(self, raw: BaseRawNLVArgs) -> None:
        self.current_index = -1
        self.configs = []
        self.output = []
        self.interactive = raw.interactive
        self.outputsuffix = raw.outputsuffix()

        # Load config(s)
        for config_i, config_file in enumerate(raw.config_files):

            with open(config_file, "r") as file:
                loaded = json.load(file, object_hook=lambda d: SimpleNamespace(**d))
                self.configs.append(self._generate_config(loaded))
                self._append_output(config_i, raw)

    def _append_output(self, config_i: int, raw: BaseRawNLVArgs):
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
            makedirs(folder)
        except:
            raise FileExistsError(
                f"Error creating directory: {folder}! Verify that {raw.outprefix[config_i]} has "
                + "an extension, so a folder with  name can be made."
            )

    def _generate_config(self, loaded) -> Config: ...

    def next(self) -> bool:
        self.current_index += 1
        return self.current_index < len(self.configs)

    def config(self) -> Config:
        return self.configs[self.current_index]

    def output_file(self, f: str, ext: str) -> str:
        output = self.output[self.current_index]
        return f"{output}-{f}{self.outputsuffix}.{ext}"


def parse_base_args(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--interactive",
        "-it",
        help="Whether the program should be interactive and display plots",
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
