import argparse
import sys

__all__ = ["tabcomplete"]


def tabcomplete(parser: argparse.ArgumentParser):
    """Bash autocomplete for subcommands and actions.
    This function is called when the script is run with
    the argument BASH_COMPLETION and the argument SUBCOMMANDS or ACTIONS {subcommand}}
    """

    def parser_choices(parser: argparse.ArgumentParser) -> dict:
        return parser._subparsers._actions[1].choices  # type: ignore

    def subparser_choices(subparser: argparse.ArgumentParser) -> dict:
        return subparser._optionals._actions[1].choices  # type: ignore

    def __get_commands() -> list[str]:
        return list(parser_choices(parser).keys())

    def __get_subcommands(command: str) -> list[str]:
        subparser = parser_choices(parser)[command]
        return list(subparser_choices(subparser).keys())

    def __get_args(command: str, subcommand: str) -> list[str]:
        subparser = parser_choices(parser)[command]
        subcommand_parser = subparser_choices(subparser)[subcommand]
        return list(subcommand_parser._option_string_actions.keys())

    argv = sys.argv[1:]

    def __raise_invalid_args():
        raise ValueError(f"Invalid tab completion arguments: {' '.join(argv)}")

    if "TAB_COMPLETION" in argv:
        if "INIT" in argv and len(argv) == 2:
            # mrh TAB_COMPLETION INIT
            __mrh_complete()
        elif "COMMANDS" in argv and len(argv) == 2:
            # mrh TAB_COMPLETION COMMANDS
            print(" ".join(__get_commands()))
        elif "SUBCOMMANDS" in argv and len(argv) == 3:
            # mrh TAB_COMPLETION SUBCOMMANDS {command}
            print(" ".join(__get_subcommands(argv[2])))
        elif "ARGS" in argv and len(argv) >= 4:
            # mrh TAB_COMPLETION ARGS {command} {subcommand}
            print(" ".join(__get_args(argv[2], argv[3])))
        # else:
        #     __raise_invalid_args()
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
    prev_prev=${COMP_WORDS[COMP_CWORD - 2]}
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
    3)
        case ${prev_prev} in
        git)
            COMPREPLY=($(compgen -W "$(mrh TAB_COMPLETION ARGS git ${prev})" -- ${cur}))
            ;;
        pipenv)
            COMPREPLY=($(compgen -W "$(mrh TAB_COMPLETION ARGS pipenv ${prev})" -- ${cur}))
            ;;
        cmd)
            COMPREPLY=($(compgen -W "$(mrh TAB_COMPLETION ARGS cmd ${prev})" -- ${cur}))
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
