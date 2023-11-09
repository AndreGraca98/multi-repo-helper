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
    "sync": "pipenv sync --dev",
    "update": "pipenv update",
    "install": "pipenv install",
}

FREE_CMDS = {"free": "{command}"}
