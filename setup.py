import os
from pathlib import Path


def path_from_home(path: Path) -> str:
    return str(path).replace(str(home), "~")


home = Path.home()
SHELLRC_FILE = Path(os.getenv("SHELLRC_FILE", default=home / ".bash_profile"))
HOME_SHELLRC_FILE = path_from_home(SHELLRC_FILE)
TABCOMPLETE_FILE = Path(os.getenv("TABCOMPLETE_FILE", default=SHELLRC_FILE))
HOME_TABCOMPLETE_FILE = path_from_home(TABCOMPLETE_FILE)
HOME_BIN_DIR = home / "bin"


if HOME_BIN_DIR.exists() and HOME_BIN_DIR.is_file():
    raise RuntimeError(f"{HOME_BIN_DIR} exists but is a file")
else:
    HOME_BIN_DIR.mkdir(exist_ok=True, parents=True)

# Create executable ~/bin/mrh from multi_repo_helper.py
home_bin_mrh = HOME_BIN_DIR / "mrh"
home_bin_mrh.touch(mode=0o755, exist_ok=True)  # rwxr-xr-x
# Overwrite if exists
home_bin_mrh.write_bytes(Path("multi_repo_helper.py").read_bytes())


# Create tabcompletion
TABCOMPLETE_TEXT = f"""
# Auto generated for mrh. Please do not edit
# >>> START tabcompletion
[ -f {path_from_home(home_bin_mrh)} ] && source /dev/stdin <<<"$(mrh BASH_COMPLETION INIT)"
# <<< END tabcompletion

"""  # noqa

if not TABCOMPLETE_FILE.exists():
    print(f"Creating {HOME_TABCOMPLETE_FILE}")
    TABCOMPLETE_FILE.touch(mode=0o644)  # rw-r--r--
    TABCOMPLETE_FILE.write_text(TABCOMPLETE_TEXT)
elif TABCOMPLETE_FILE.read_text().find(TABCOMPLETE_TEXT) == -1:
    # If file exists but doesn't have the tabcomplete text, add it
    print(f"Adding tabcomplete to {HOME_TABCOMPLETE_FILE}")
    text = TABCOMPLETE_FILE.read_text()
    TABCOMPLETE_FILE.write_text(text + TABCOMPLETE_TEXT)
else:
    print(f"Tabcomplete already exists in {HOME_TABCOMPLETE_FILE}")

# Add tabcomplete to shellrc
SHELLRC_TEXT = f"[ -f {HOME_TABCOMPLETE_FILE} ] && source {HOME_TABCOMPLETE_FILE}"

if SHELLRC_FILE == TABCOMPLETE_FILE:
    print(
        f"SHELLRC_FILE={path_from_home(SHELLRC_FILE)} and "
        f"TABCOMPLETE_FILE={path_from_home(TABCOMPLETE_FILE)} "
        "are the same file"
    )
elif not SHELLRC_FILE.exists():
    raise RuntimeError(f"{SHELLRC_FILE=} does not exist")
elif not SHELLRC_FILE.is_file():
    raise RuntimeError(f"{SHELLRC_FILE=} exists but is not a file")
elif SHELLRC_FILE.read_text().find(SHELLRC_TEXT) == -1:
    # If file exists but doesn't have the tabcomplete text, add it
    print(f"Adding tabcomplete to {HOME_SHELLRC_FILE}")
    text = SHELLRC_FILE.read_text()
    SHELLRC_FILE.write_text(text + SHELLRC_TEXT)
else:
    print(f"Tabcomplete already exists in {HOME_SHELLRC_FILE}")

# Make sure the ~/bin directory is in the PATH
if not (PATH := os.getenv("PATH")):
    raise RuntimeError("PATH is not set")

if PATH.find(str(HOME_BIN_DIR)) == -1:
    print(f"Adding {HOME_BIN_DIR} to PATH in {HOME_SHELLRC_FILE}")
    text = SHELLRC_FILE.read_text()
    SHELLRC_FILE.write_text(text + f"\nexport PATH={HOME_BIN_DIR}:$PATH\n")


print(f"Setup done! Please run `source {HOME_SHELLRC_FILE}` to enable tabcompletion")
