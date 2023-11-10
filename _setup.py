import os
import shutil
from pathlib import Path

from _mrh.logger import get_logger

_log = get_logger(__name__)


def setup_executable():
    def path_from_home(path: Path) -> str:
        return str(path).replace(str(home), "~")

    home = Path.home()
    SHELLRC_FILE = Path(os.getenv("SHELLRC_FILE", default=home / ".bash_profile"))
    HOME_SHELLRC_FILE = path_from_home(SHELLRC_FILE)
    TABCOMPLETION_FILE = Path(os.getenv("TABCOMPLETION_FILE", default=SHELLRC_FILE))
    HOME_TABCOMPLETION_FILE = path_from_home(TABCOMPLETION_FILE)
    HOME_BIN_DIR = home / "bin"

    _mrh_bin_dir = HOME_BIN_DIR / "_mrh"
    if _mrh_bin_dir.exists() and _mrh_bin_dir.is_file():
        raise RuntimeError(f"{_mrh_bin_dir} exists but is a file")
    else:
        _mrh_bin_dir.mkdir(exist_ok=True, parents=True)

    # Create executable ~/bin/mrh from mrh.py
    home_bin_mrh = HOME_BIN_DIR / "mrh"
    home_bin_mrh.touch(mode=0o755, exist_ok=True)  # rwxr-xr-x
    # Overwrite if exists
    home_bin_mrh.write_bytes(Path("mrh.py").read_bytes())
    # Copy source code from _mrh directory to ~/bin/_mrh
    shutil.copytree("_mrh", _mrh_bin_dir, dirs_exist_ok=True)

    # Create tabcompletion
    TABCOMPLETION_TEXT = f"""
# Auto generated for mrh. Please do not edit
# >>> START tabcompletion
[ -f {path_from_home(home_bin_mrh)} ] && source /dev/stdin <<<"$(mrh TAB_COMPLETION INIT)"
# <<< END tabcompletion
    """  # noqa

    if not TABCOMPLETION_FILE.exists():
        _log.info(f"creating {HOME_TABCOMPLETION_FILE}")
        TABCOMPLETION_FILE.touch(mode=0o644)  # rw-r--r--
        TABCOMPLETION_FILE.write_text(TABCOMPLETION_TEXT)
    elif TABCOMPLETION_FILE.read_text().find(TABCOMPLETION_TEXT) == -1:
        # If file exists but doesn't have the tabcomplete text, add it
        _log.info(f"adding mrh tabcompletion to {HOME_TABCOMPLETION_FILE}")
        text = TABCOMPLETION_FILE.read_text()
        TABCOMPLETION_FILE.write_text(text + TABCOMPLETION_TEXT)
    else:
        _log.warning(f"mrh tabcompletion already exists in {HOME_TABCOMPLETION_FILE}")

    # Add tabcomplete to shellrc
    SHELLRC_TEXT = (
        f"[ -f {HOME_TABCOMPLETION_FILE} ] && source {HOME_TABCOMPLETION_FILE}"
    )

    if SHELLRC_FILE == TABCOMPLETION_FILE:
        _log.warning(
            f"SHELLRC_FILE={path_from_home(SHELLRC_FILE)} and "
            f"TABCOMPLETE_FILE={path_from_home(TABCOMPLETION_FILE)} "
            "are the same file"
        )
    elif not SHELLRC_FILE.exists():
        raise RuntimeError(f"{SHELLRC_FILE=} does not exist")
    elif not SHELLRC_FILE.is_file():
        raise RuntimeError(f"{SHELLRC_FILE=} exists but is not a file")
    elif SHELLRC_FILE.read_text().find(SHELLRC_TEXT) == -1:
        # If file exists but doesn't have the tabcomplete text, add it
        _log.info(f"adding {SHELLRC_TEXT!r} to {HOME_SHELLRC_FILE}")
        text = SHELLRC_FILE.read_text()
        SHELLRC_FILE.write_text(text + SHELLRC_TEXT)
    else:
        _log.warning(f"{SHELLRC_TEXT!r} already exists in {HOME_SHELLRC_FILE}")

    # Make sure the ~/bin directory is in the PATH
    if not (PATH := os.getenv("PATH")):
        raise RuntimeError("PATH is not set")

    if PATH.find(str(HOME_BIN_DIR)) == -1:
        _log.info(f"Adding {HOME_BIN_DIR} to PATH in {HOME_SHELLRC_FILE}")
        text = SHELLRC_FILE.read_text()
        SHELLRC_FILE.write_text(text + f"\nexport PATH={HOME_BIN_DIR}:$PATH\n")

    _log.info(
        f"Setup done! Please run `source {HOME_SHELLRC_FILE}` to enable tabcompletion"
    )


if __name__ == "__main__":
    setup_executable()
