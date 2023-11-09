import os
import subprocess
from pathlib import Path

from mrh.colors import cs
from mrh.commands import COMMANDS
from mrh.logger import get_logger

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


def filter_dirs(directory: Path, filter_str: str) -> set[Path]:
    """Get all directories in a given directory that match a
    filter string and are git repositories"""
    directory = directory.resolve()
    return set(filter(lambda p: (p / ".git").is_dir(), directory.glob(filter_str)))


def get_filtered_dirs(directory: Path, filter_strs: list[str]) -> list[Path]:
    total_filtered: set[Path] = set()
    for filter_str in filter_strs:
        filtered = filter_dirs(directory, filter_str)
        total_filtered.update(filtered)
    return sorted(total_filtered)


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


def run_cmd(repo: Path, cmd: str):
    print_str = f"{fname(repo.name)}\n{fcode('$ '+cmd)}\n"
    cmd_str = f'printf "{print_str}" && {cmd}'
    with cd(repo):
        return subprocess.run(cmd_str, capture_output=True, shell=True)
