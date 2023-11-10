import subprocess
from pathlib import Path

from .commands import COMMANDS
from .logger import get_logger
from .terminal import fname, run_cmd

_log = get_logger(__name__)

__all__ = ["Action"]


class Action:
    def __init__(self, command: str, subcommand: str, **kwargs) -> None:
        self._command = command
        self._subcommand = subcommand
        self._kwargs = kwargs

    @property
    def cmd_str(self) -> str:
        return COMMANDS[self._command][self._subcommand].format(**self._kwargs)

    def __call__(self, repo: Path) -> subprocess.CompletedProcess:
        return self.run(repo)

    def run(self, repo: Path) -> subprocess.CompletedProcess:
        _log.info(f"Running on {fname(repo.name)}")
        return run_cmd(repo, self.cmd_str)

    def __str__(self) -> str:
        return self.cmd_str

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._command}, {self._subcommand})"
