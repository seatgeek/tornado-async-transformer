import os
import re
import sys
from pathlib import Path
from typing import List, Tuple
import argparse

import libcst as cst
from libcst import CSTVisitorT

from tornado_async_transformer import TornadoAsyncTransformer, TransformError


def transform_file(visitor: CSTVisitorT, filename: str) -> None:
    with open(filename, "r") as python_file:
        python_source = python_file.read()

    try:
        source_tree = cst.parse_module(python_source)
    except Exception as e:
        print("{} failed parse: {}".format(filename, str(e)))
        return

    try:
        visited_tree = source_tree.visit(visitor)
    except TransformError as e:
        print("{} failed transform: {}".format(filename, str(e)))
        return

    if not visited_tree.deep_equals(source_tree):
        with open(filename, "w") as python_file:
            python_file.write(visited_tree.code)


def collect_files(base: str) -> Tuple[str, ...]:
    """
    Collect all python files under a base directory.
    """

    def is_python_file(path: str) -> bool:
        return bool(os.path.isfile(path) and re.search(r"\.pyi?$", path))

    if is_python_file(base):
        return (base,)

    if os.path.isdir(base):
        python_files: List[str] = []
        for root, dirs, filenames in os.walk(base):
            full_filenames = (f"{root}/{filename}" for filename in filenames)
            python_files += [
                full_filename
                for full_filename in full_filenames
                if is_python_file(full_filename)
            ]
        return tuple(python_files)

    return tuple()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Codemod for converting legacy tornado @gen.coroutine syntax to python3.5+ native async/await"
    )
    parser.add_argument(
        "bases",
        type=str,
        nargs="+",
        help="Files and directories (recursive) including python files to be modified.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    python_files: List[str] = []
    for base in args.bases:
        python_files += collect_files(base)

    for python_file in python_files:
        transform_file(TornadoAsyncTransformer(), python_file)


if __name__ == "__main__":
    main()
