import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path

from logger import get_logger

_log = get_logger(__name__)


@dataclass
class Configuration:
    filter: list[str] = field(default_factory=list)
    verbose: bool = False
    no_notify: bool = False


@dataclass
class ConfigurationReader:
    path: Path

    def read(self) -> Configuration:
        if not self.path.is_file():
            _log.warning(f"Config file {str(self.path)!r} not found")
            return Configuration()

        if self.path.read_text() == "":
            _log.warning(f"Config file {str(self.path)!r} is empty")
            return Configuration()

        with open(self.path, "r") as f:
            _log.info(f"Reading config file {str(self.path)!r}")
            return Configuration(**json.load(f))


def get_parser():
    class JoinValuesAction(argparse.Action):
        """Action to join multiple values into one string for argparse"""

        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.values = []

        def __call__(self, parser, namespace, values, option_string=None):
            self.values.append(values)
            setattr(namespace, self.dest, " ".join(self.values))

    class ConfigurationAction(argparse.Action):
        def __call__(self, parser, namespace, value, option_string=None):
            path = Path(value).resolve()
            setattr(namespace, self.dest, ConfigurationReader(path).read())

    def add_top_level_args(parser: argparse.ArgumentParser):
        parser.add_argument(
            "--cfg",
            "--config",
            type=str,
            default=Configuration(),
            dest="config",
            action=ConfigurationAction,
            help="Config file to use",
        )

    here = Path.cwd().resolve()
    command_parser = argparse.ArgumentParser(
        description=f"Actions for all git repos in {here}",
    )
    sub_parsers = command_parser.add_subparsers(dest="command")

    git_parser = sub_parsers.add_parser(name="git", help="Run a git command")
    git_sub_parsers = git_parser.add_subparsers(dest="subcommand")
    git_sub_parsers.add_parser("fetch", help="Fetch remotes")
    git_sub_parsers.add_parser("pull", help="Pull remotes")
    git_sub_parsers.add_parser("push", help="Push changes")
    git_add_parser = git_sub_parsers.add_parser("add", help="Add changes")
    git_add_parser.add_argument(
        "files",
        nargs="+",
        default=[],
        action="extend",
        help="Files to add",
        metavar="PATH ...",
    )
    git_commit_parser = git_sub_parsers.add_parser("commit", help="Commit changes")
    git_commit_parser.add_argument(
        "message",
        nargs="+",
        default=[],
        action="extend",
        help="Commit message",
        metavar="MESSAGE",
    )
    git_checkout_parser = git_sub_parsers.add_parser("checkout", help="Checkout branch")
    git_checkout_parser.add_argument("branch", type=str, help="Branch to checkout")
    git_stash_parser = git_sub_parsers.add_parser("stash", help="Stash changes")
    git_stash_parser.add_argument(
        "-a", "--all", action="store_true", dest="all", help="Stash all changes"
    )
    git_stash_parser.add_argument(
        "-m", "--message", dest="message", help="Stash message"
    )
    git_sub_parsers.add_parser("unstash", help="Apply last stash changes")

    #
    # git_sub_parsers.add_parser("status", help="Show status")
    # git_sub_parsers.add_parser("diff", help="Show diff")
    # git_sub_parsers.add_parser("log", help="Show log")
    # git_sub_parsers.add_parser("branch", help="Show branches")
    # git_sub_parsers.add_parser("tag", help="Show tags")
    # git_sub_parsers.add_parser("remote", help="Show remotes")
    # git_sub_parsers.add_parser("config", help="Show config")
    # git_sub_parsers.add_parser("clean", help="Clean repo")
    # git_sub_parsers.add_parser("reset", help="Reset repo")
    # git_sub_parsers.add_parser("revert", help="Revert repo")
    for sub_parser in git_sub_parsers.choices.values():
        add_top_level_args(sub_parser)

    return command_parser

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
        choices={"dev", "latest", "master"},
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
    venv_parser.add_argument(
        "-u",
        "--update",
        dest="update",
        action="store_true",
        help="Update the virtual environment",
    )
    venv_parser.add_argument(
        "-i",
        "--install",
        dest="install",
        action="store_true",
        help="Install the virtual environment",
    )
    add_top_level_args(venv_parser)

    cmd_parser = sub_parsers.add_parser(
        "cmd",
        help="Run a free text command in each repo",
        description=f"Run a free text command in each repo of {here}",
    )
    cmd_parser.add_argument("command", type=str, help="Command to run")
    add_top_level_args(cmd_parser)

    return command_parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    print(args)
