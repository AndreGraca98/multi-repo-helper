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


def get_repos(directory: Path) -> list[Path]:
    return sorted(filter(is_git_repo, directory.glob("*")))


def cmd_str(repo: Path, cmd: str) -> str:
    """Combine the git repo and command to better print the output

    Args:
        repo (Path): The git repo
        cmd (str): The command to run

    Returns:
        str: The combined command
    """
    print_str = f"Git Repo => {repo.name}\nCommand: $ {cmd}\n\n"
    return f'printf "{print_str}" && {cmd}'


def run_cmd(repo: Path, cmd: str):
    return subprocess.run(cmd_str(repo, cmd), capture_output=True, shell=True)


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
        for repo in get_repos(repos_parent):
            print("*", repo.name)


def run_free_cmd(git_dir: Path, /, command: str) -> subprocess.CompletedProcess:
    print(f"[{git_dir.name}] Running command: {command}")
    with CD(git_dir):
        return run_cmd(git_dir, command)


class GitActions:
    """Git actions for a single repo"""

    @staticmethod
    def fetch_remotes(repo: Path) -> subprocess.CompletedProcess:
        print(f"Fetching remotes for {repo.name}")
        with CD(repo):
            # Fetch all remotes in parallel with 4 threads
            return run_cmd(repo, "git fetch -j4 --all")

    @staticmethod
    def pull_remotes(repo: Path) -> subprocess.CompletedProcess:
        print(f"Pulling remotes for {repo.name}")
        with CD(repo):
            # Pull all remotes in parallel with 4 threads
            return run_cmd(repo, "git pull -j4 --all")

    @staticmethod
    def checkout_branch(repo: Path, branch: str) -> subprocess.CompletedProcess:
        print(f"Checkout git branch for {repo.name}")
        with CD(repo):
            return run_cmd(repo, f"git checkout {branch}")

    @staticmethod
    def stash_changes(repo: Path) -> subprocess.CompletedProcess:
        print(f"Stashing changes for {repo.name}")
        with CD(repo):
            return run_cmd(repo, "git stash")

    @staticmethod
    def apply_stash_changes(repo: Path) -> subprocess.CompletedProcess:
        print(f"Applying last stash changes for {repo.name}")
        with CD(repo):
            return run_cmd(repo, "git stash pop")

    @staticmethod
    def commit(repo: Path, msg: str) -> subprocess.CompletedProcess:
        print(f"Comiting changes for {repo.name}")
        with CD(repo):
            return run_cmd(repo, f'git commit -m "{msg}"')

    @staticmethod
    def push(repo: Path) -> subprocess.CompletedProcess:
        print(f"Pushing changes for {repo.name}")
        with CD(repo):
            return run_cmd(repo, "git push")


class VenvActions:
    """Actions for virtual environments"""

    def update(git_dir: Path) -> subprocess.CompletedProcess:
        print(f"Updating virtual environment for {git_dir.name}")
        raise NotImplementedError
        with CD(git_dir):
            return run_cmd(git_dir, "pipenv update --dev")

    def remove(git_dir: Path) -> subprocess.CompletedProcess:
        print(f"Removing virtual environment for {git_dir.name}")
        raise NotImplementedError
        with CD(git_dir):
            return run_cmd(git_dir, "pipenv --rm")

    def install(git_dir: Path) -> subprocess.CompletedProcess:
        print(f"Installing virtual environment for {git_dir.name}")
        raise NotImplementedError
        with CD(git_dir):
            return run_cmd(
                git_dir, "pip install pip pipenv --upgrade && pipenv install --dev"
            )


def get_parser():
    here = Path.cwd().resolve()

    def add_verbose(parser: argparse.ArgumentParser):
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="Print verbose output"
        )

    parser = argparse.ArgumentParser(description=f"Actions for all git repos in {here}")
    sub_parsers = parser.add_subparsers(dest="subcommand")

    info_parser = sub_parsers.add_parser(
        "info",
        help="Top level repos info",
        description=f"Top level info for repos in {here}",
    )
    info_parser.add_argument("-l", "--list", action="store_true", help="List repos")
    add_verbose(info_parser)

    cmd_parser = sub_parsers.add_parser(
        "cmd",
        help="Run a free text command in each repo",
        description=f"Run a free text command in each repo of {here}",
    )
    cmd_parser.add_argument("command", type=str, help="Command to run")
    add_verbose(cmd_parser)

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
        "--apply_stash",
        action="store_true",
        dest="apply_stash",
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
        "--commit",
        type=str,
        default="",
        dest="commit",
        help="Commit changes with message",
    )
    git_parser.add_argument("-P", "--push", action="store_true", help="Push changes")
    add_verbose(git_parser)

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
    add_verbose(venv_parser)

    return parser


def get_actions(
    parser: argparse.ArgumentParser,
) -> tuple[bool, str, list[Callable]]:
    """Get a list of actions to perform in each repo

    Args:
        parser (argparse.ArgumentParser): Parser

    Returns:
        tuple[bool, str, list[Callable]]: verbose?, subcommand?, list of actions
    """
    args = parser.parse_args()
    argsd = dict(args._get_kwargs())

    verbose = argsd.pop("verbose", False)
    subcommand = argsd.pop("subcommand")

    if not subcommand:
        parser.print_help()
        exit(0)

    if not any(argsd.values()):
        # Print help if no action is specified
        subparsers = parser._subparsers._actions[1].choices
        print(subparsers[subcommand].format_help())
        exit(0)

    actions = []

    if subcommand == "info":
        if argsd["list"]:
            actions.append(InfoActions.list_repos)

    elif subcommand == "git":
        if argsd["fetch"]:
            actions.append(GitActions.fetch_remotes)
        if argsd["stash"]:
            actions.append(GitActions.stash_changes)
        if argsd["pull"]:
            actions.append(GitActions.pull_remotes)
        if argsd["apply_stash"]:
            actions.append(GitActions.apply_stash_changes)
        if argsd["checkout"]:
            actions.append(
                partial(GitActions.checkout_branch, branch=argsd["checkout"])
            )
        if argsd["commit"]:
            actions.append(partial(GitActions.commit, msg=argsd["commit"]))
        if argsd["push"]:
            actions.append(GitActions.push)

    elif subcommand == "venv":
        if argsd["update"]:
            actions.append(VenvActions.update)
        if argsd["remove"]:
            actions.append(VenvActions.remove)
        if argsd["install"]:
            actions.append(VenvActions.install)

    elif subcommand == "cmd":
        actions.append(partial(run_free_cmd, command=argsd["command"]))

    return verbose, subcommand, actions


def main(parser: argparse.ArgumentParser):
    here = Path.cwd().resolve()
    repos = get_repos(here)

    verbose, subcommand, actions = get_actions(parser)

    # TODO: (maybe?) filter out repos
    for action in actions:
        if subcommand == "info":
            action(here)
            continue

        with Pool(4) as p:
            results = p.map(action, repos)
            print("=" * 100)
            for r in results:
                if not verbose and r.returncode == 0:
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
