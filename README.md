# Multi git repository helper

:warning: Work in progress :warning:

This is a tool to help when dealing with multiple repositories for a single
project where you may need to perform the same action on all the git
repositories

## How to install

Run (in `multi-repo-helper/`):

```bash
# Load mrh from single file
SHELLRC_FILE=~/.bash_profile python setup.py
# Load mrh from tab completion file
SHELLRC_FILE=~/.bash_profile TABCOMPLETION_FILE=~/.bash_completion python setup.py

# Or just use the Makefile
make setup-bash
make setup-zsh
...
```

## How to use

Can be used in any folder that has git repositories

### Create a config file

If no config file is found `mrh` will use default values

```bash
echo '{"filter":["*repo1*", "*repo2*"], "verbose":false, "no_notify":true}' > .mrh.json
```

### Chain commands

```bash
$ mrh git fetch && mrh git add file1.txt file2.txt && mrh git commit "feat: my super feature" && mrh git push
<<< "fetches all repos, adds file1 and file2, commits with a message and finaly pushes to remote" >>>
```

### Use arguments from a file

```bash
$ echo '{"filter":["*my-repo*"], "verbose":false, "no_notify":true}' > my-cfg-file.json
$ cat my-cfg-file.json
{
    "filter": [
        "*my-repo*"
    ],
    "verbose": false,
    "no_notify": true
}
$ mrh pipenv install --cfg my-cfg-file.json
<<< "Installs the virtual environment only for repositories that match *my-repo*" >>>
```

### Usefull commands

```bash
$ cat cbs-ms.json
{
    "verbose": false,
    "filter": [
        "core",
        "icn*",
        "doc*gen*",
        "*inter*",
        "time*",
        "*api*"
    ]
}
# Pull all the repos
$ mrh git pull --cfg cbs-ms.json
# Update all the lock files
$ mrh pipenv update --cfg cbs-ms.json
# Test all services
$ mrh cmd free "make test" --cfg cbs-ms.json
# Add all pipfile lock changes, commit with message and push to origin
$ mrh git add Pipfile.lock --cfg cbs-ms.json
$ mrh git commit "chore: update piplock" --cfg cbs-ms.json
$ mrh git push --cfg cbs-ms.json
```
