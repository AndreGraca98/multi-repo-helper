# Multi git repository helper

:warning: Work in progress :warning:

This is a tool to help when dealing with multiple repositories for a single project where you may need to perform the same action on all the git repos

## How to install

Run (in `multi-repo-helper/`):

```bash
# Load mrh from single file
SHELLRC_FILE=~/.bash_profile python setup.py
# Load mrh from tab completion file
SHELLRC_FILE=~/.bash_profile TABCOMPLETE_FILE=~/.bash_completion python setup.py
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
$ mrh git --fetch --add file1.txt --add file2.txt --commit "feat: my super feature" --push
<<< "fetches all repos, adds file1 and file2, commits with a message and finaly pushes to remote" >>>
```

### Use arguments from a file

```bash
$ echo -e "--install\n--filter\nrepo1\nrepo2\n--verbose" > myargs
$ cat myargs 
--install
--filter
repo1
repo2
--verbose
$ mrh venv @myargs
<<< "Installs the virtual environment only for repo1 and repo2" >>>
```

### Usefull commands

```bash
$ cat filter-ms
--filter
core
icn*
doc*gen*
*inter*
time*
*api*
# Pull all the repos
$ mrh git --pull @filter-ms
# Update all the lock files
$ mrh venv --update @filter-ms
# Test all services
$ mrh cmd "make test" @filter-ms
# Add all pipfile lock changes, commit with message and push to origin
$ mrh git --add "Pipfile.lock" --commit "chore: update piplock" --push  @filter-ms
```
