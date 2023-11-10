import argparse
import sys

__all__ = ["tabcomplete"]


def tabcomplete(parser: argparse.ArgumentParser):
    """Bash autocomplete for subcommands and actions.
    This function is called when the script is run with
    the argument BASH_COMPLETION and the argument SUBCOMMANDS or ACTIONS {subcommand}}
    """

    def subparser_choices(parser: argparse.ArgumentParser) -> dict:
        return parser._subparsers._actions[1].choices  # type: ignore

    def __get_commands() -> list[str]:
        return list(subparser_choices(parser).keys())

    def __get_subcommands(command: str) -> list[str]:
        subparser = subparser_choices(parser)[command]
        subcommands = subparser._optionals._actions[1].choices.keys()
        return list(subcommands)

    argv = sys.argv[1:]

    def __raise_invalid_args():
        raise ValueError(f"Invalid tab completion arguments: {' '.join(argv)}")

    if "TAB_COMPLETION" in argv:
        if "INIT" in argv:
            __mrh_complete()
        elif "COMMANDS" in argv:
            if len(sys.argv) != 3:
                __raise_invalid_args()
            print(" ".join(__get_commands()))
        elif "SUBCOMMANDS" in argv:
            if len(sys.argv) != 4:
                __raise_invalid_args()
            print(" ".join(__get_subcommands(sys.argv[3])))
        else:
            __raise_invalid_args()
        exit(0)


def __mrh_complete():
    print(
        """

# MRH
# START: Bash tab completion for multi_repo_helper
# Do not edit the following line; it is used by multi_repo_helper
_mrh_complete() {
    local cur prev
    cur=${COMP_WORDS[COMP_CWORD]}
    prev=${COMP_WORDS[COMP_CWORD - 1]}
    case ${COMP_CWORD} in
    1)
        COMPREPLY=($(compgen -W "$(mrh TAB_COMPLETION COMMANDS)" -- ${cur}))
        ;;
    2)
        case ${prev} in
        git)
            COMPREPLY=($(compgen -W "$(mrh TAB_COMPLETION SUBCOMMANDS git)" -- ${cur}))
            ;;
        pipenv)
            COMPREPLY=($(compgen -W "$(mrh TAB_COMPLETION SUBCOMMANDS pipenv)" -- ${cur}))
            ;;
        cmd)
            COMPREPLY=($(compgen -W "$(mrh TAB_COMPLETION SUBCOMMANDS cmd)" -- ${cur}))
            ;;
        *)
            COMPREPLY=()
            ;;
        esac
        ;;
    *)
        COMPREPLY=($(compgen -f -- ${cur}))

        ;;
    esac
}
complete -F _mrh_complete mrh
# END: Bash tab completion for multi_repo_helper

"""  # noqa: E501
    )
