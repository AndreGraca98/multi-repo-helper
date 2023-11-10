import os
import shutil
from pathlib import Path

from _mrh.logger import get_logger

_log = get_logger(__name__)


def setup_executable():
    def path_from_home(path: Path) -> str:
        return str(path).replace(str(home), "~")

    MRH_SOURCE_FILE = Path("mrh.py")
    MRH_SOURCE_FOLDER = Path("_mrh")

    home = Path.home()
    HOME_BIN_DIR = home / "bin"
    MRH_BIN_EXECUTABLE_FILE = HOME_BIN_DIR / "mrh"
    MRH_BIN_SOURCE_FOLDER = HOME_BIN_DIR / "_mrh"

    shellrc_file = os.getenv("SHELLRC_FILE")
    assert shellrc_file, "SHELLRC_FILE is required"
    SHELLRC_FILE = Path(shellrc_file)
    HOME_SHELLRC_FILE = path_from_home(SHELLRC_FILE)

    ADD_COMPLETION: bool = False
    tabcompletion_file = os.getenv("COMPLETION_FILE")
    if tabcompletion_file:
        # If COMPLETION_FILE is set, add tabcompletion
        COMPLETION_FILE = Path(tabcompletion_file)
        ADD_COMPLETION: bool = True

    def add_bin_executable():
        if MRH_BIN_SOURCE_FOLDER.exists() and MRH_BIN_SOURCE_FOLDER.is_file():
            raise RuntimeError(f"{MRH_BIN_SOURCE_FOLDER} exists but is a file")
        else:
            # create ~/bin directory if it doesn't exist
            MRH_BIN_SOURCE_FOLDER.mkdir(exist_ok=True, parents=True)

        # Create executable ~/bin/mrh from mrh.py
        MRH_BIN_EXECUTABLE_FILE.touch(mode=0o755, exist_ok=True)  # rwxr-xr-x
        # Overwrite if exists
        MRH_BIN_EXECUTABLE_FILE.write_bytes(MRH_SOURCE_FILE.read_bytes())
        # Copy source code from _mrh directory to ~/bin/_mrh
        shutil.copytree(MRH_SOURCE_FOLDER, MRH_BIN_SOURCE_FOLDER, dirs_exist_ok=True)

        # Make sure the ~/bin directory is in the PATH
        if not (PATH := os.getenv("PATH")):
            raise RuntimeError("PATH is not set")

        if PATH.find(str(HOME_BIN_DIR)) == -1:
            _log.info(f"Adding {HOME_BIN_DIR} to PATH in {HOME_SHELLRC_FILE}")
            text = SHELLRC_FILE.read_text()
            SHELLRC_FILE.write_text(text + f"\nexport PATH={HOME_BIN_DIR}:$PATH\n")

    def add_completion():
        # Create tabcompletion
        COMPLETION_TEXT = f"""
# Auto generated for mrh. Please do not edit
# >>> START tabcompletion
[ -f {path_from_home(MRH_BIN_EXECUTABLE_FILE)} ] && source /dev/stdin <<<"$(mrh COMPLETION INIT)"
# <<< END tabcompletion
"""  # noqa
        assert ADD_COMPLETION
        assert COMPLETION_FILE
        HOME_COMPLETION_FILE = path_from_home(COMPLETION_FILE)

        if not COMPLETION_FILE.exists():
            _log.info(f"creating {HOME_COMPLETION_FILE}")
            COMPLETION_FILE.touch(mode=0o644)  # rw-r--r--
            COMPLETION_FILE.write_text(COMPLETION_TEXT)
        elif COMPLETION_FILE.read_text().find(COMPLETION_TEXT) == -1:
            # If file exists but doesn't have the tabcomplete text, add it
            _log.info(f"adding mrh tabcompletion to {HOME_COMPLETION_FILE}")
            text = COMPLETION_FILE.read_text()
            COMPLETION_FILE.write_text(text + COMPLETION_TEXT)
        else:
            _log.warning(f"mrh tabcompletion already exists in {HOME_COMPLETION_FILE}")

        # Add tabcomplete to shellrc
        SHELLRC_TEXT = f"[ -f {HOME_COMPLETION_FILE} ] && source {HOME_COMPLETION_FILE}"

        # Check if SHELLRC_FILE is COMPLETION_FILE
        if SHELLRC_FILE == COMPLETION_FILE:
            _log.warning(
                f"SHELLRC_FILE={path_from_home(SHELLRC_FILE)} and "
                f"COMPLETION_FILE={path_from_home(COMPLETION_FILE)} "
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

    add_bin_executable()
    if ADD_COMPLETION:
        add_completion()

    _log.info(
        f"Setup done! Please run `source {HOME_SHELLRC_FILE}` to enable tab completion"
    )


if __name__ == "__main__":
    setup_executable()
