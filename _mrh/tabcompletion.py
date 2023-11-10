import argparse
import sys

__all__ = ["tabcomplete"]


def tabcomplete(parser: argparse.ArgumentParser):
    """Bash autocomplete for subcommands and actions.
    This function is called when the script is run when:
    - mrh COMPLETION INIT
    - mrh COMPLETION COMMANDS
    - mrh COMPLETION SUBCOMMANDS {command}
    - mrh COMPLETION ARGS {command} {subcommand}
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

    if "COMPLETION" in argv:
        if "INIT" in argv and len(argv) == 2:
            # mrh COMPLETION INIT
            __mrh_complete()
        elif "COMMANDS" in argv and len(argv) == 2:
            # mrh COMPLETION COMMANDS
            print(" ".join(__get_commands()))
        elif "SUBCOMMANDS" in argv and len(argv) == 3:
            # mrh COMPLETION SUBCOMMANDS {command}
            print(" ".join(__get_subcommands(argv[2])))
        elif "ARGS" in argv and len(argv) >= 4:
            # mrh COMPLETION ARGS {command} {subcommand}
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
    local cur first second
    cur=${COMP_WORDS[COMP_CWORD]}
    [[ len_words=${#COMP_WORDS[@]} -gt 0 ]] && first=${COMP_WORDS[1]} || first=""
    [[ len_words=${#COMP_WORDS[@]} -gt 1 ]] && second=${COMP_WORDS[2]} || second=""

    case ${COMP_CWORD} in
    1)
        COMPREPLY=($(compgen -W "$(mrh COMPLETION COMMANDS)" -- ${cur}))
        ;; # Gives commands
    2)
        case ${first} in
        git | pipenv | cmd)
            COMPREPLY=($(compgen -W "$(mrh COMPLETION SUBCOMMANDS ${first})" -- ${cur}))
            ;; # Gives subcommands for a command
        *)
            COMPREPLY=()
            ;;
        esac
        ;;
    *)
        case ${cur} in
        -*)
            COMPREPLY=($(compgen -W "$(mrh COMPLETION ARGS ${first} ${second})" -- ${cur}))
            ;; # Gives args for subcommands of a command
        *)
            COMPREPLY=($(compgen -f -- ${cur})) # If no matches complete with files
            ;;
        esac
        ;;
    esac
}
complete -F _mrh_complete mrh
# END: Bash tab completion for multi_repo_helper

"""  # noqa: E501
    )
