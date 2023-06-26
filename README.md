# Multi git repository helper

:warning: Work in progress :warning:

This is a tool to help when dealing with multiple repositories for a single project where you may need to perform the same action on all the git repos

## How to install

Run (in `multi-repo-helper/`):

```bash
. setup.sh
```

## How to use

Can be used in any folder that has git repositories

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
