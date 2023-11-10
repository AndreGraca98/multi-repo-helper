# Multi git repository helper

![badge](https://img.shields.io/github/v/tag/AndreGraca98/multi-repo-helper?logo=python&logoColor=yellow&label=version)

This is a tool to help when dealing with multiple repositories for a single
project where you may need to perform the same action on all the git
repositories

## How to install

### From pip

```bash
# Use default options
pip install git+https://github.com/AndreGraca98/multi-repo-helper.git
# Or pass the locations
SHELLRC_FILE=~/.bash_profile COMPLETION_FILE=~/.bash_completion pip install git+https://github.com/AndreGraca98/multi-repo-helper.git
```

### From local mrh repository

```bash
# Create mrh without tabcompletion
SHELLRC_FILE=~/.bash_profile python _setup.py
# Create mrh with tabcompletion
SHELLRC_FILE=~/.bash_profile COMPLETION_FILE=~/.bash_completion python _setup.py

# Or just use the Makefile
make setup-bash
make setup-zsh
...
```

Possible installation options (as environment variables)

| Options         | Description                                                  | Type | Required | Example            |
| --------------- | ------------------------------------------------------------ | ---- | -------- | ------------------ |
| SHELLRC_FILE    | The file that loads the terminal                             | str  | Yes      | ~/.bash_profile    |
| COMPLETION_FILE | The tab completions file (can be the same as *SHELLRC_FILE*) | str  | No       | ~/.bash_completion |

Note: If *COMPLETION_FILE* is not set, mrh will not have tab completion

## How to use

Can be used in any folder that has git repositories

### Create a config file

If no config file is passed `mrh` tries to read a default config file `.mrh.json`. If the file is not found, it will use default values.

```bash
echo '{"filter":["*repo1*", "*repo2*"], "verbose":false, "no_notify":true}' > .mrh.json
```

Possible configuration options (in the *.json* file)

| Options   | Description                                    | Type      | Required | Example |
| --------- | ---------------------------------------------- | --------- | -------- | ------- |
| filter    | A list of filters to gather repositories       | list[str] | No       | ---     |
| verbose   | Verbose mode                                   | bool      | No       | ---     |
| no_notify | Don't notify when the command finishes running | bool      | No       | ---     |
| pool_size | How many processes to run at the same time     | int       | No       | ---     |

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
