import argparse
from pathlib import Path
from typing import Iterable

from .commands import COMMANDS
from .configuration import DEFAULT_CONFIGURATION_READER, ConfigurationReader
from .logger import get_logger

__all__ = ["get_parser"]

_log = get_logger(__name__)


class ExtendAndJoinStrAction(argparse.Action):
    """Action class for extending and joining string arguments"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.values = []

    def __call__(self, parser, namespace, values: list, option_string=None):
        self.values.extend(values)
        setattr(namespace, self.dest, " ".join(self.values))


class ConfigurationAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        path = Path(value).resolve()
        setattr(namespace, self.dest, ConfigurationReader(path).read())


def add_top_level_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-c",
        "--cfg",
        type=str,
        default=DEFAULT_CONFIGURATION_READER.read(),
        dest="config",
        action=ConfigurationAction,
        help="Config file to use",
    )


class subcommand:
    """Context manager for adding subcommands to a parser"""

    def __init__(self, sub_parser, name: str):
        self.name = name
        parser = sub_parser.add_parser(name=name, help=f"Run a {name} command")
        self.sub_parser = parser.add_subparsers(dest="subcommand", required=True)

    def __enter__(self):
        return self.sub_parser

    def __exit__(self, exc_type, exc_value, exc_traceback):
        sub_parsers = self.sub_parser.choices

        _subcommands_sanity_check(
            sub_parsers.keys(),
            COMMANDS[self.name].keys(),
            parser_name=self.name,
        )
        for git_sub_parser in sub_parsers.values():
            add_top_level_args(git_sub_parser)


def add_git_parser(sub_parser: argparse._SubParsersAction):
    with subcommand(sub_parser, "git") as git_sub_parser:
        git_sub_parser.add_parser("fetch", help="Fetch remotes")
        git_sub_parser.add_parser("pull", help="Pull remotes")
        git_sub_parser.add_parser("push", help="Push changes")
        git_add_parser = git_sub_parser.add_parser("add", help="Add changes")
        git_add_parser.add_argument(
            "files",
            nargs="+",
            default=[],
            action=ExtendAndJoinStrAction,
            help="Files to add",
            metavar="PATH ...",
        )
        git_commit_parser = git_sub_parser.add_parser("commit", help="Commit changes")
        git_commit_parser.add_argument(
            "message",
            nargs="+",
            default=[],
            action=ExtendAndJoinStrAction,
            help="Commit message",
            metavar="MESSAGE",
        )
        git_checkout_parser = git_sub_parser.add_parser(
            "checkout", help="Checkout branch"
        )
        git_checkout_parser.add_argument("branch", type=str, help="Branch to checkout")
        # TODO
        # git_stash_parser = git_sub_parsers.add_parser("stash", help="Stash changes")
        # git_stash_parser.add_argument(
        #     "-a", "--all", action="store_true", dest="all", help="Stash all changes"
        # )
        # git_stash_parser.add_argument(
        #     "-m", "--message", dest="message", help="Stash message"
        # )
        # git_sub_parsers.add_parser("unstash", help="Apply last stash changes")

        # TODO
        # git_sub_parsers.add_parser("branch", help="Show branches")
        # git_sub_parsers.add_parser("tag", help="Show tags")
        # git_sub_parsers.add_parser("status", help="Show status")
        # Dangerous commands
        # git_sub_parsers.add_parser("clean", help="Clean repo")
        # git_sub_parsers.add_parser("reset", help="Reset repo")
        # git_sub_parsers.add_parser("revert", help="Revert repo")


def add_pipenv_parser(sub_parser: argparse._SubParsersAction):
    with subcommand(sub_parser, "pipenv") as pipenv_sub_parser:
        pipenv_sub_parser.add_parser("location", help="Get location of virtualenv")
        pipenv_sub_parser.add_parser("lock", help="Lock dependencies")
        pipenv_sub_parser.add_parser("remove", help="Remove virtualenv")
        pipenv_sub_parser.add_parser("sync", help="Sync dependencies")
        pipenv_sub_parser.add_parser("update", help="Update dependencies")
        pipenv_sub_parser.add_parser("install", help="Install dependencies")


def add_cmd_parser(sub_parser: argparse._SubParsersAction):
    with subcommand(sub_parser, "cmd") as cmd_sub_parser:
        cmd_free_sub_parser = cmd_sub_parser.add_parser(
            "free", help="Run a free command"
        )
        cmd_free_sub_parser.add_argument(
            "free_command", help="Command to run", metavar='"COMMAND"'
        )
        # cmd_test_sub_parser = cmd_sub_parser.add_parser(
        #     "test", help="Run a test command"
        # )
        # cmd_test_sub_parser.add_argument(
        #     "test_command", help="Command to run [FOR TESTING]", metavar='"COMMAND"'
        # )


def get_parser():
    command_parser = argparse.ArgumentParser(
        description=f"Actions for all git repos in {Path.cwd().resolve()}",
    )
    sub_parsers = command_parser.add_subparsers(dest="command", required=True)

    add_git_parser(sub_parsers)
    add_pipenv_parser(sub_parsers)
    add_cmd_parser(sub_parsers)

    return command_parser


def _subcommands_sanity_check(
    parser_keys: Iterable[str], commands_keys: Iterable[str], *, parser_name: str = ""
):
    if difference := set(parser_keys) ^ set(commands_keys):
        raise ValueError(
            f"Parser {parser_name} keys and commands keys do not match. {difference=}"
        )


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    print(args)
