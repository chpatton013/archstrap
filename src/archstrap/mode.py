import logging
import subprocess
from abc import ABC, abstractmethod


class Mode(ABC):
    def on_begin(self):
        pass

    @abstractmethod
    def on_section(self, section: str):
        pass

    @abstractmethod
    def on_command(self, command: str):
        pass

    def on_end(self):
        pass


def make_mode(name: str) -> Mode:
    """
    Instantiate the appropriate Mode based on the specified name.
    """
    if name == "exec":
        return ExecMode()
    elif name == "dryrun":
        return DryrunMode()
    elif name == "shell":
        return ShellMode()
    else:
        raise ValueError(f"Unknown mode '{name}'")


class ExecMode(Mode):
    def on_section(self, section: str):
        logging.info("SECTION %s", section)

    def on_command(self, command: str):
        logging.info("COMMAND %s", command)
        subprocess.check_call(command, shell=True)


class DryrunMode(Mode):
    def on_section(self, section: str):
        logging.info("SECTION %s", section)

    def on_command(self, command: str):
        logging.info("COMMAND %s", command)


class ShellMode(Mode):
    def on_begin(self):
        print("#!/usr/bin/bash")
        print("set -xeuo pipefail")

    def on_section(self, section: str):
        logging.info("SECTION %s", section)
        print()
        print("#", section)

    def on_command(self, command: str):
        logging.info("COMMAND %s", command)
        print(command)
