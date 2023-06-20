#!/usr/bin/env python3

"""
How to install

Add the following to your ~/.bashrc:
PATH=$HOME/bin:$PATH

Run:
chmod +x multi_repo_helper.py
mkdir -p ~/bin
cp multi_repo_helper.py ~/bin/multi_repo_helper
. ~/.bashrc

"""

import argparse
import os
import subprocess
from functools import partial
from multiprocessing import Pool
from pathlib import Path
from typing import Callable


def is_git_repo(path: Path) -> bool:
    return (path / ".git").is_dir()


def is_dir(path: Path) -> bool:
    return path.is_dir()


def get_dirs(
    directory: Path, filter_str: str = "*", git_only: bool = False
) -> set[Path]:
    directory = directory.resolve()
    return set(filter(is_git_repo if git_only else is_dir, directory.glob(filter_str)))


def get_filtered_dirs(
    directory, filter_strs: list[str], git_only: bool = False
) -> set[Path]:
    filtered_dirs = []
    for f in filter_strs:
        filtered_dirs.extend(get_dirs(directory, f, git_only=git_only))
    return set(filtered_dirs)


def run_cmd(repo: Path, cmd: str):
    print_str = f"Git Repo => {repo.name}\nCommand: $ {cmd}\n\n"
    cmd_str = f'printf "{print_str}" && {cmd}'
    with CD(repo):
        return subprocess.run(cmd_str, capture_output=True, shell=True)


class CD:
    """Context manager for changing the current working directory"""

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.cwd = Path.cwd()
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.cwd)


class InfoActions:
    """Top level info actions"""

    def list_repos(repos_parent: Path):
        print(f"Listing repos in {repos_parent}")
        for repo in get_dirs(repos_parent, git_only=True):
            print("*", repo.name)


def run_free_cmd(repo: Path, /, command: str) -> subprocess.CompletedProcess:
    print(f"[{repo.name}] Running command: {command}")
    return run_cmd(repo, command)


GIT_CMDS = {
    "fetch": "git fetch -j4 --all",
    "pull": "git pull -j4 --all",
    "checkout": "git checkout {branch}",
    "stash": "git stash",
    "unstash": "git stash pop",
    "commit": 'git commit -m "{message}"',
    "push": "git push",
}


def git_cmd_factory(command: str, **kwargs):
    def run_git_cmd(repo: Path) -> subprocess.CompletedProcess:
        cmd = GIT_CMDS[command].format(**kwargs)
        return run_cmd(repo, cmd)

    return run_git_cmd


VENV_CMDS = {
    "update": "pipenv update --dev",
    "remove": "pipenv --rm",
    "install": "pip install pip pipenv --upgrade && pipenv install --dev",
}


def venv_cmd_factory(command: str, **kwargs):
    def run_venv_cmd(repo: Path) -> subprocess.CompletedProcess:
        raise NotImplementedError
        cmd = VENV_CMDS[command].format(**kwargs)
        return run_cmd(repo, cmd)

    return run_venv_cmd


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
        "-c",
        "--checkout",
        type=str,
        choices={"dev", "presentation"},
        default=None,
        dest="checkout",
        help="Checkout branch",
    )
    git_parser.add_argument(
        "-C",
        "--COMMIT",
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
            actions.append(git_cmd_factory("fetch"))
        if argsd["stash"]:
            actions.append(git_cmd_factory("stash"))
        if argsd["pull"]:
            actions.append(git_cmd_factory("pull"))
        if argsd["unstash"]:
            actions.append(git_cmd_factory("unstash"))
        if argsd["checkout"]:
            actions.append(git_cmd_factory("checkout", branch=argsd["checkout"]))
        if argsd["commit"]:
            actions.append(git_cmd_factory("commit", message=argsd["commit"]))
        if argsd["push"]:
            actions.append(git_cmd_factory("push"))

    elif subcommand == "venv":
        if argsd["update"]:
            actions.append(venv_cmd_factory("update"))
        if argsd["remove"]:
            actions.append(venv_cmd_factory("remove"))
        if argsd["install"]:
            actions.append(venv_cmd_factory("install"))

    elif subcommand == "cmd":
        actions.append(partial(run_free_cmd, command=argsd["command"]))

    return args, actions


def main(parser: argparse.ArgumentParser):
    here = Path.cwd().resolve()
    args, actions = get_actions(parser)

    filtered_repos = get_filtered_dirs(here, args.filter, not args.all_dirs)

    # TODO: (maybe?) filter out repos
    for action in actions:
        if args.subcommand == "info":
            action(here)
            continue

        with Pool(4) as p:
            results = p.map(action, filtered_repos)
            print("=" * 100)
            for r in results:
                if not args.verbose and r.returncode == 0:
                    continue
                print(
                    "SUCCESS" if r.returncode == 0 else "FAILED",
                    "\nStdout:",
                    r.stdout.decode(),
                    "\nStderr:",
                    r.stderr.decode(),
                    "\n" + "=" * 100,
                )


if __name__ == "__main__":
    parser = get_parser()
    main(parser)
