_mrh() {
    local cur prev
    cur=${COMP_WORDS[COMP_CWORD]}
    prev=${COMP_WORDS[COMP_CWORD - 1]}

    case ${COMP_CWORD} in
    1)
        COMPREPLY=($(compgen -W "$(mrh BASH_COMPLETION SUBCOMMANDS)" -- ${cur}))
        ;;
    2)
        case ${prev} in
        git)
            COMPREPLY=($(compgen -W "$(mrh BASH_COMPLETION ACTIONS git)" -- ${cur}))
            ;;
        venv)
            COMPREPLY=($(compgen -W "$(mrh BASH_COMPLETION ACTIONS venv)" -- ${cur}))
            ;;
        cmd)
            COMPREPLY=($(compgen -W "$(mrh BASH_COMPLETION ACTIONS cmd)" -- ${cur}))
            ;;
        esac
        ;;
    *)
        COMPREPLY=()
        ;;
    esac
}
complete -F _mrh mrh
