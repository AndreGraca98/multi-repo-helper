#!/usr/bin/env python3

"""
Disclaimer: This file is a big monolith so that
we don't need to import from other files.

How to install

Add the following to your ~/.bashrc or prefered shell config file:
PATH=$HOME/bin:$PATH

Run:
chmod +x multi_repo_helper.py
mkdir -p ~/bin
cp multi_repo_helper.py ~/bin/multi_repo_helper

"""

import argparse
import os
import subprocess
from multiprocessing import Pool
from pathlib import Path
from typing import Callable

GIT_CMDS = {
    "fetch": "git fetch -j4 --all",
    "pull": "git pull -j4 --all",
    "checkout": "git checkout {branch}",
    "stash": "git stash",
    "unstash": "git stash pop",
    "add": "git add {files_str}",  # files_str is a string of files separated by spaces
    "commit": 'git commit -m "{message}"',
    "push": "git push",
}


VENV_CMDS = {
    "update": "pipenv update --dev",
    "remove": "pipenv --rm",
    "install": "pip install pip pipenv --upgrade && pipenv install --dev",
}

FREE_CMDS = {"free": "{command}"}


# Console pretty printing
class cs:
    """Console styles"""

    # Styles
    END = "\33[0m"
    BOLD = "\33[1m"
    MUTE = "\33[2m"
    ITALIC = "\33[3m"
    UNDERLINE = "\33[4m"
    BLINK = "\33[5m"
    SELECTED = "\33[7m"
    STRIKE = "\33[9m"
    # Foreground colors
    BLACK = "\33[30m"
    RED = "\33[31m"
    GREEN = "\33[32m"
    YELLOW = "\33[33m"
    BLUE = "\33[34m"
    MAGENTA = "\33[35m"
    CYAN = "\33[36m"
    WHITE = "\33[37m"
    # Backgroud colors
    BBLACK = "\33[40m"
    BRED = "\33[41m"
    BGREEN = "\33[42m"
    BYELLOW = "\33[43m"
    BBLUE = "\33[44m"
    BMAGENTA = "\33[45m"
    BCYAN = "\33[46m"
    BWHITE = "\33[47m"
    # Muted foregroud colors
    MBLACK = "\33[90m"
    MRED = "\33[91m"
    MGREEN = "\33[92m"
    MYELLOW = "\33[93m"
    MBLUE = "\33[94m"
    MMAGENTA = "\33[95m"
    MCYAN = "\33[96m"
    MWHITE = "\33[97m"
    # Muted backgroud colors
    MBBLACK = "\33[100m"
    MBRED = "\33[101m"
    MBGREEN = "\33[102m"
    MBYELLOW = "\33[103m"
    MBBLUE = "\33[104m"
    MBMAGENTA = "\33[105m"
    MBCYAN = "\33[106m"
    MBWHITE = "\33[107m"

    def __init__(self, *styles: str):
        self.styles = styles

    def __call__(self, text: str) -> str:
        style = "".join(self.styles)
        return f"{style}{text}{cs.END}"


title = cs(cs.BOLD, cs.UNDERLINE, cs.YELLOW)
underline = cs(cs.UNDERLINE)
name = cs(cs.BOLD, cs.UNDERLINE, cs.MUTE, cs.BBLUE)
code = cs(cs.ITALIC, cs.MUTE, cs.GREEN)
error = cs(cs.BOLD, cs.BLINK, cs.RED)
success = cs(cs.BOLD, cs.GREEN)


# Utils
def is_dir(path: Path) -> bool:
    return path.is_dir()


def is_git_repo(path: Path) -> bool:
    return (path / ".git").is_dir()


def get_dirs(
    directory: Path, filter_str: str = "*", git_only: bool = False
) -> set[Path]:
    directory = directory.resolve()
    return set(filter(is_git_repo if git_only else is_dir, directory.glob(filter_str)))


def get_filtered_dirs(
    directory, filter_strs: list[str], git_only: bool = False
) -> list[Path]:
    filtered_dirs = []
    for f in filter_strs:
        filtered_dirs.extend(get_dirs(directory, f, git_only=git_only))
    return sorted(set(filtered_dirs))


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, path):
        self.path = path.resolve()

    def __enter__(self):
        self.cwd = Path.cwd()
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.cwd)


def run_cmd(repo: Path, cmd: str):
    print_str = f"{name(repo.name)}\n{code('$ '+cmd)}\n"
    cmd_str = f'printf "{print_str}" && {cmd}'
    with cd(repo):
        return subprocess.run(cmd_str, capture_output=True, shell=True)


# Action/Command classes
class Actions:
    def __init__(self, action: str, **kwargs) -> None:
        self.action = action
        self.kwargs = kwargs

    @property
    def cmd(self) -> str:
        raise NotImplementedError

    def __call__(self, repo: Path) -> subprocess.CompletedProcess:
        print(f"Current repo: {name(repo.name)} ")
        return run_cmd(repo, self.cmd)

    def __str__(self) -> str:
        return self.cmd

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.action}, {self.kwargs})"


class Git(Actions):
    @property
    def cmd(self) -> str:
        return GIT_CMDS[self.action].format(**self.kwargs)


class Venv(Actions):
    @property
    def cmd(self) -> str:
        raise NotImplementedError
        return VENV_CMDS[self.action].format(**self.kwargs)


class Free(Actions):
    @property
    def cmd(self) -> str:
        return FREE_CMDS[self.action].format(**self.kwargs)


class InfoActions:
    """Top level info actions"""

    def list_repos(repos_parent: Path):
        print(f"Listing repos in {title(repos_parent)}")
        for repo in sorted(get_dirs(repos_parent, git_only=True)):
            print("*", name(repo.name))


def get_parser():
    here = Path.cwd().resolve()

    def add_top_level_args(parser: argparse.ArgumentParser):
        parser.add_argument(
            "--verbose", action="store_true", help="Print verbose output"
        )
        parser.add_argument(
            "--filter",
            type=str,
            nargs="+",
            default=["*"],
            help="Filter repos. WARNING: if using the wildcard * "
            'don\'t forget to add " around it (like "*") , '
            "otherwise it will get the cwd files/dirs.",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            dest="all_dirs",
            help="Run on all directories, even if they are not a git repository.",
        )

    parser = argparse.ArgumentParser(description=f"Actions for all git repos in {here}")
    sub_parsers = parser.add_subparsers(dest="subcommand")

    info_parser = sub_parsers.add_parser(
        "info",
        help="Top level repos info",
        description=f"Top level info for repos in {here}",
    )
    info_parser.add_argument("-l", "--list", action="store_true", help="List repos")
    add_top_level_args(info_parser)

    cmd_parser = sub_parsers.add_parser(
        "cmd",
        help="Run a free text command in each repo",
        description=f"Run a free text command in each repo of {here}",
    )
    cmd_parser.add_argument("command", type=str, help="Command to run")
    add_top_level_args(cmd_parser)

    git_parser = sub_parsers.add_parser(
        "git",
        help="Run a git command in each repo",
        description=f"Run a git command in each repo of {here}",
    )
    git_parser.add_argument("-f", "--fetch", action="store_true", help="Fetch remotes")
    git_parser.add_argument("-p", "--pull", action="store_true", help="Pull remotes")
    git_parser.add_argument(
        "-s", "--stash", action="store_true", dest="stash", help="Stash changes"
    )
    git_parser.add_argument(
        "-a",
        "--unstash",
        action="store_true",
        dest="unstash",
        help="Apply last stash changes",
    )
    git_parser.add_argument(
        "--checkout",
        type=str,
        choices={"dev", "presentation"},
        default=None,
        dest="checkout",
        help="Checkout branch",
    )
    git_parser.add_argument(
        "--add",
        type=str,
        nargs="?",
        const=".",
        default=None,
        action="append",
        dest="add",
        help="Add changes",
    )
    git_parser.add_argument(
        "--commit",
        type=str,
        dest="commit",
        help="Commit changes with message",
    )
    git_parser.add_argument(
        "-P", "--PUSH", action="store_true", dest="push", help="Push changes"
    )
    add_top_level_args(git_parser)

    venv_parser = sub_parsers.add_parser(
        "venv",
        help="Run a virtual environment command in each repo",
        description=f"Run a virtual environment command in each repo of {here}",
        allow_abbrev=True,
    )
    venv_parser.add_argument("-u", "--update", action="store_true", help="Update venvs")
    venv_parser.add_argument("-r", "--remove", action="store_true", help="Remove venvs")
    venv_parser.add_argument(
        "-i", "--install", action="store_true", help="Install venvs"
    )
    add_top_level_args(venv_parser)

    return parser


def get_actions(
    parser: argparse.ArgumentParser,
) -> tuple[argparse.Namespace, list[Callable]]:
    """Get a list of actions to perform in each repo

    Args:
        parser (argparse.ArgumentParser): Parser

    Returns:
        tuple[argparse.Namespace, list[Callable]]: args, list of actions
    """
    args = parser.parse_args()
    argsd = dict(args._get_kwargs())

    # Pop to make help printing easier
    if "verbose" in argsd:
        argsd.pop("verbose")
    if "filter" in argsd:
        argsd.pop("filter")
    if "all_dirs" in argsd:
        argsd.pop("all_dirs")
    subcommand = argsd.pop("subcommand")

    if not subcommand:
        # Print main help if no subcommand specified
        parser.print_help()
        exit(0)

    if not any(argsd.values()):
        # Print subcommand help if no action is specified
        subparsers = parser._subparsers._actions[1].choices
        print(subparsers[subcommand].format_help())
        exit(0)

    actions = []

    if subcommand == "info":
        if argsd["list"]:
            actions.append(InfoActions.list_repos)

    elif subcommand == "git":
        if argsd["fetch"]:
            actions.append(Git("fetch"))
        if argsd["stash"]:
            actions.append(Git("stash"))
        if argsd["pull"]:
            actions.append(Git("pull"))
        if argsd["unstash"]:
            actions.append(Git("unstash"))
        if argsd["checkout"]:
            actions.append(Git("checkout", branch=argsd["checkout"]))
        if argsd["add"]:
            actions.append(Git("add", files_str=" ".join((argsd["add"]))))
        if argsd["commit"]:
            actions.append(Git("commit", message=argsd["commit"]))
        if argsd["push"]:
            actions.append(Git("push"))

    elif subcommand == "venv":
        if argsd["update"]:
            actions.append(Venv("update"))
        if argsd["remove"]:
            actions.append(Venv("remove"))
        if argsd["install"]:
            actions.append(Venv("install"))

    elif subcommand == "cmd":
        actions.append(Free("free", command=argsd["command"]))

    return args, actions


def main(parser: argparse.ArgumentParser):
    here = Path.cwd().resolve()
    args, actions = get_actions(parser)

    filtered_repos = get_filtered_dirs(here, args.filter, not args.all_dirs)

    for cmd in actions:
        if args.subcommand == "info":
            cmd(here)
            continue

        print(f"Running {code(cmd)} in {len(filtered_repos)} repos...")
        with Pool(4) as p:
            results = p.map(cmd, filtered_repos)
            print("=" * 100)
            for r in results:
                if not args.verbose and r.returncode == 0:
                    continue

                text = ""
                text += success("[SUCCESS]") if r.returncode == 0 else error("[FAILED]")
                text += f"\n{underline('Stdout')}: {r.stdout.decode()}"
                text += f"\n{underline('Stderr')}: {r.stderr.decode()}\n"
                text += "=" * 100

                print(text)


if __name__ == "__main__":
    parser = get_parser()
    main(parser)
    # print(get_actions(parser))
