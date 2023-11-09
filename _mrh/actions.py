import os
import subprocess
from pathlib import Path

from .colors import cs
from .commands import COMMANDS
from .logger import get_logger

_log = get_logger(__name__)

__all__ = ["Action"]

fname = cs(cs.BOLD, cs.UNDERLINE, cs.MUTE, cs.BBLUE)
fcode = cs(cs.ITALIC, cs.MUTE, cs.GREEN)


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
        kwargs = ", ".join(f"{k}={v!r}" for k, v in self._kwargs.items())
        if kwargs:
            kwargs = ", " + kwargs
        return (
            f"{self.__class__.__name__}({self._command}, "
            f"{self._subcommand}{kwargs})"
        )


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, path: str | Path):
        self.path = Path(path).resolve()
        assert self.path.is_dir()
        self.cwd = Path.cwd()

    def __enter__(self):
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.cwd)


def run_cmd(repository: Path, cmd: str):
    print_str = f"{fname(repository.name)}\n{fcode('$ '+cmd)}\n"
    cmd_str = f'printf "{print_str}" && {cmd}'
    with cd(repository):
        return subprocess.run(cmd_str, capture_output=True, shell=True)
