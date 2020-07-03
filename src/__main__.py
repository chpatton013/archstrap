#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sys
from typing import List, Optional

from archstrap import run
from archstrap.specification import Specification, make_specification


def runtime_dir():
    script_dir = os.path.abspath(os.path.dirname(__file__))
    if getattr(sys, "frozen", False):
        return script_dir
    else:
        return os.path.join(script_dir, "..")


ARCHSTRAP_VERSION = "0.0.1"

README_PATH = os.path.join(runtime_dir(), "README.md")

DEFAULT_INSTALL_ROOT = "/mnt"


class DocumentationAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        with open(README_PATH, "r") as f:
            print(f.read().rstrip())
        parser.exit()


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="archstrap",
        description="",
    )
    parser.register("action", "doc", DocumentationAction)
    parser.add_argument("--doc", action="doc")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {ARCHSTRAP_VERSION}",
    )
    parser.add_argument(
        "specification",
        default=None,
        help="Path to specification file (default: stdin)",
    )
    parser.add_argument(
        "--install-root",
        default=DEFAULT_INSTALL_ROOT,
        help=
        "Path to install Arch Llinux system to (default: {DEFAULT_INSTALL_ROOT})",
    )
    parser.add_argument(
        "--mode",
        choices=("exec", "dryrun", "shell"),
        default="shell",
        help="Operational mode (default: shell)",
    )
    log_level_group = parser.add_mutually_exclusive_group()
    log_level_group.add_argument(
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        dest="log_level",
        help="Show debug log messages (default: info, warning, and error)",
    )
    log_level_group.add_argument(
        "--quiet",
        action="store_const",
        const=logging.WARNING,
        dest="log_level",
        help=
        "Only show warning and error log messages (default: info, warning, and error)",
    )
    parser.set_defaults(log_level=logging.INFO)
    return parser.parse_args(argv)


def load_spec(specification: Optional[str]) -> Specification:
    if not specification or specification == "-":
        spec = json.load(sys.stdin)
    with open(specification, "r") as f:
        spec = json.load(f)
    return make_specification(spec)


def main(argv: List[str]):
    args = parse_args(argv)

    logging.basicConfig(level=args.log_level)

    spec = load_spec(args.specification)

    run(spec, args.mode, args.install_root)

    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
