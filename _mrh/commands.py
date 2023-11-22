COMMANDS = dict(
    git=dict(
        fetch="git fetch -j4 --all",
        pull="git pull -j4 --all",
        add="git add {files}",  # files is a string of files separated by spaces
        commit='git commit -m "{message}"',
        push="git push",
        checkout="git checkout {branch}",
        restore="git restore {files}",  # files is a string of files separated by spaces
        # stash="git stash",
        # unstash="git stash pop",
    ),
    pipenv=dict(
        location="pipenv --venv",
        lock="pipenv lock",
        remove="pipenv --rm",
        sync="pipenv sync --dev",
        update="pipenv update",
        install="pipenv install --dev",
    ),
    cmd=dict(
        free="{free_command}",
        # test="{test_command}",
    ),
)
