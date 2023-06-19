# Multi git repository helper

## How to install

Add the following to your ~/.bashrc: `PATH=$HOME/bin:$PATH`

Run (in current directory):

```bash
chmod +x multi_repo_helper.py
mkdir -p ~/bin
cp multi_repo_helper.py ~/bin/multi_repo_helper
. ~/.bashrc
```

## How to use

Can be used in any folder that has git repositories

```bash
multi_repo_helper info -l
```
