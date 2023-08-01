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
cp multi_repo_helper.py ~/bin/mrh

"""

import argparse
import os
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path
from typing import Callable

GIT_CMDS = {
    "fetch": "git fetch -j4 --all",
    "pull": "git pull -j4 --all",
    "checkout": "git checkout {branch}",
    "stash": "git stash",
    "unstash": "git stash pop",
    "add": "git add {files}",  # files is a string of files separated by spaces
    "commit": 'git commit -m "{message}"',
    "push": "git push",
}


VENV_CMDS = {
    "location": "pipenv --venv",
    "lock": "pipenv lock",
    "remove": "pipenv --rm",
    "sync": "pipenv sync",
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


ftitle = cs(cs.BOLD, cs.UNDERLINE, cs.YELLOW)
funderline = cs(cs.UNDERLINE)
fstrike = cs(cs.STRIKE)
fname = cs(cs.BOLD, cs.UNDERLINE, cs.MUTE, cs.BBLUE)
fcode = cs(cs.ITALIC, cs.MUTE, cs.GREEN)
ferror = cs(cs.BOLD, cs.BLINK, cs.RED)
fsuccess = cs(cs.BOLD, cs.GREEN)
fhelp = cs(cs.YELLOW, cs.MUTE)


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

    def __init__(self, path: str | Path):
        self.path = Path(path).resolve()

    def __enter__(self):
        self.cwd = Path.cwd()
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.cwd)


def run_cmd(repo: Path, cmd: str):
    print_str = f"{fname(repo.name)}\n{fcode('$ '+cmd)}\n"
    cmd_str = f'printf "{print_str}" && {cmd}'
    with cd(repo):
        return subprocess.run(cmd_str, capture_output=True, shell=True)


# Action/Command classes
class Action:
    """Action class for executing commands on a repo or top level directory"""

    class Level:
        TOP = "top"
        REPO = "repo"

    level = NotImplemented  # Top level or repo level action

    def __init__(self, action: str, **kwargs) -> None:
        self.action = action
        self.kwargs = kwargs

    @property
    def cmd(self) -> str:
        raise NotImplementedError

    def __call__(self, repo: Path) -> subprocess.CompletedProcess:
        print(f"Current repo: {fname(repo.name)} ")
        return run_cmd(repo, self.cmd)

    def __str__(self) -> str:
        return self.cmd

    def __repr__(self) -> str:
        kwargs = ", ".join(f"{k}={v}" for k, v in self.kwargs.items())
        if kwargs:
            kwargs = ", " + kwargs
        return (
            # f"Action level: {self.level} => "
            f"{self.__class__.__name__}({self.action}{kwargs})"
        )


class Git(Action):
    level = Action.Level.REPO

    @property
    def cmd(self) -> str:
        return GIT_CMDS[self.action].format(**self.kwargs)


class Venv(Action):
    level = Action.Level.REPO

    @property
    def cmd(self) -> str:
        return VENV_CMDS[self.action].format(**self.kwargs)


class Free(Action):
    level = Action.Level.REPO

    @property
    def cmd(self) -> str:
        return FREE_CMDS[self.action].format(**self.kwargs)


def get_parser():
    class JoinValuesAction(argparse.Action):
        """Action to join multiple values into one string for argparse"""

        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.values = []

        def __call__(self, parser, namespace, values, option_string=None):
            self.values.append(values)
            setattr(namespace, self.dest, " ".join(self.values))

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

    parser = argparse.ArgumentParser(
        description=f"Actions for all git repos in {here}",
        fromfile_prefix_chars="@",
    )
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
        "-u",
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
        action=JoinValuesAction,
        dest="add",
        help="Add changes. Use < --add > to add all changes or "
        '< --add "file1" --add "file2" > to add specific files.',
        metavar="PATH ...",
    )

    git_parser.add_argument(
        "--commit",
        type=str,
        dest="commit",
        help="Commit changes",
        metavar='"MESSAGE"',
    )
    git_parser.add_argument(
        "-P",
        "--push",
        action="store_true",
        dest="push",
        help="Push changes",
    )
    add_top_level_args(git_parser)

    venv_parser = sub_parsers.add_parser(
        "venv",
        help="Run a virtual environment command in each repo",
        description=f"Run a virtual environment command in each repo of {here}",
        allow_abbrev=True,
    )
    venv_parser.add_argument(
        "--location",
        dest="location",
        action="store_true",
        help="Show location of virtual environment",
    )
    venv_parser.add_argument(
        "-l",
        "--lock",
        dest="lock",
        action="store_true",
        help="Lock dependencies",
    )
    venv_parser.add_argument(
        "-r",
        "--remove",
        dest="remove",
        action="store_true",
        help="Remove virtual environment",
    )
    venv_parser.add_argument(
        "-s",
        "--sync",
        dest="sync",
        action="store_true",
        help="Install dependencies from lock file",
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
        print(fhelp(parser.format_help()))
        exit(0)

    if not any(argsd.values()):
        # Print subcommand help if no action is specified
        subparsers = parser._subparsers._actions[1].choices
        print(fhelp(subparsers[subcommand].format_help()))
        exit(0)

    actions = []

    if subcommand == "git":
        if argsd["fetch"]:
            actions.append(Git("fetch"))
        if argsd["stash"]:
            actions.append(Git("stash"))
        if argsd["checkout"]:
            actions.append(Git("checkout", branch=argsd["checkout"]))
        if argsd["pull"]:
            actions.append(Git("pull"))
        if argsd["unstash"]:
            actions.append(Git("unstash"))
        if argsd["add"]:
            actions.append(Git("add", files=argsd["add"]))
        if argsd["commit"]:
            actions.append(Git("commit", message=argsd["commit"]))
        if argsd["push"]:
            actions.append(Git("push"))

    elif subcommand == "venv":
        if argsd["location"]:
            actions.append(Venv("location"))
        if argsd["lock"]:
            actions.append(Venv("lock"))
        if argsd["remove"]:
            actions.append(Venv("remove"))
        if argsd["sync"]:
            actions.append(Venv("sync"))

    elif subcommand == "cmd":
        actions.append(Free("free", command=argsd["command"]))

    return args, actions


def multi_action(action: Action, repos: list[Path], verbose: bool = False):
    print(f"Running {fcode(action)} in {len(repos)} repos...")
    with Pool(10) as p:
        results = p.map(action, repos)
        print("=" * 100)
        for r in results:
            if not verbose and r.returncode == 0:
                continue

            txt = ""
            txt += ferror("[FAILED]") if r.returncode else fsuccess("[SUCCESS]")
            txt += f"\n{funderline('Stdout')}: {r.stdout.decode()}"
            txt += f"\n{funderline('Stderr')}: {r.stderr.decode()}\n"
            txt += fstrike("=" * 100)

            print(txt)


def main(parser: argparse.ArgumentParser):
    here = Path.cwd().resolve()
    args, actions = get_actions(parser)

    filtered_repos = get_filtered_dirs(here, args.filter, not args.all_dirs)

    for action in actions:
        if action.level == Action.Level.TOP:
            print(f"Running {fcode(action)} in top level directory...")
            action()
        else:
            multi_action(action, filtered_repos, args.verbose)

    notify(actions)


def notify(actions):
    import platform

    if platform.system() == "Darwin":
        notify_macos(actions)
    elif platform.system() == "Linux":
        notify_linux(actions)
    elif platform.system() == "Windows":
        notify_windows(actions)
    else:
        raise NotImplementedError


def notify_macos(actions):
    # # Use macos voice to notify when the actions are finished
    # subprocess.run("say Finished", shell=True)
    # Use macos dialog to notify when the actions are finished
    app = '"System Events"'
    actions_str = "\n".join(map(lambda a: f"\u2022\t{a}", actions))
    text = f'"Multi repo helper finished running actions:\n{actions_str}"'
    OK = '{"OK"}'
    subprocess.run(
        f"osascript -e 'tell application {app} to display "
        f"dialog {text} buttons {OK}' >/dev/null",
        shell=True,
    )


def notify_linux(actions):
    ...


def notify_windows(actions):
    ...


def __bash_autocomplete(parser: argparse.ArgumentParser):
    """Bash autocomplete for subcommands and actions.
    This function is called when the script is run with
    the argument BASH_COMPLETION and the argument SUBCOMMANDS or ACTIONS {subcommand}}
    """

    def __get_subcommands():
        return parser._subparsers._actions[1].choices.keys()

    def __get_subcommand_actions(subcommand: str):
        actions = parser._subparsers._actions[1].choices[subcommand]._optionals._actions
        options = []
        for action in actions:
            options.extend(action.option_strings)
        return options

    if "BASH_COMPLETION" in sys.argv[1:]:
        if "SUBCOMMANDS" in sys.argv[1:]:
            if len(sys.argv) != 3:
                raise ValueError(
                    r"Invalid bash completion argument: "
                    r"python multi_repo_helper.py SUBCOMMANDS"
                )
            print(" ".join(__get_subcommands()))
        elif "ACTIONS" in sys.argv[1:]:
            if len(sys.argv) != 4:
                raise ValueError(
                    r"Invalid bash completion argument: "
                    r"python multi_repo_helper.py ACTIONS {subcommand}"
                )
            print(" ".join(__get_subcommand_actions(sys.argv[3])))
        else:
            raise ValueError(
                r"Invalid bash completion argument: "
                r"'python multi_repo_helper.py SUBCOMMANDS' "
                r"or 'python multi_repo_helper.py ACTIONS {subcommand}'"
            )
        exit(0)


if __name__ == "__main__":
    parser = get_parser()
    __bash_autocomplete(parser)
    main(parser)
    # print(get_actions(parser))
