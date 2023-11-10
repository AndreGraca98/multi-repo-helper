__all__ = ["cs"]


# Console pretty printing
import os
import subprocess
from pathlib import Path


class cs:
    """Console styles"""

    # Styles
    END = "\33[0m"
    BOLD = "\33[1m"
    MUTE = "\33[2m"
    ITALIC = "\33[3m"
    UNDERLINE = "\33[4m"
    BLINK = "\33[5m"
    SELECTED = "\33[7m"
    STRIKE = "\33[9m"
    # Foreground colors
    BLACK = "\33[30m"
    RED = "\33[31m"
    GREEN = "\33[32m"
    YELLOW = "\33[33m"
    BLUE = "\33[34m"
    MAGENTA = "\33[35m"
    CYAN = "\33[36m"
    WHITE = "\33[37m"
    # Backgroud colors
    BBLACK = "\33[40m"
    BRED = "\33[41m"
    BGREEN = "\33[42m"
    BYELLOW = "\33[43m"
    BBLUE = "\33[44m"
    BMAGENTA = "\33[45m"
    BCYAN = "\33[46m"
    BWHITE = "\33[47m"
    # Muted foregroud colors
    MBLACK = "\33[90m"
    MRED = "\33[91m"
    MGREEN = "\33[92m"
    MYELLOW = "\33[93m"
    MBLUE = "\33[94m"
    MMAGENTA = "\33[95m"
    MCYAN = "\33[96m"
    MWHITE = "\33[97m"
    # Muted backgroud colors
    MBBLACK = "\33[100m"
    MBRED = "\33[101m"
    MBGREEN = "\33[102m"
    MBYELLOW = "\33[103m"
    MBBLUE = "\33[104m"
    MBMAGENTA = "\33[105m"
    MBCYAN = "\33[106m"
    MBWHITE = "\33[107m"

    def __init__(self, *styles: str):
        self.styles = styles

    def __call__(self, text: str) -> str:
        style = "".join(self.styles)
        return f"{style}{text}{cs.END}"


fmagenta = cs(cs.MAGENTA, cs.BOLD)
fred = cs(cs.RED)
fyellow = cs(cs.YELLOW)
fblue = cs(cs.BLUE)
fgreen = cs(cs.GREEN, cs.MUTE)

#
fname = cs(cs.BOLD, cs.UNDERLINE, cs.MUTE, cs.BBLUE)
fcode = cs(cs.ITALIC, cs.MUTE, cs.GREEN)


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, path: str | Path):
        self.path = Path(path).resolve()
        assert self.path.is_dir()
        self.cwd = Path.cwd()

    def __enter__(self):
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.cwd)


def run_cmd(repository: Path, cmd: str):
    print_str = f"{fname(repository.name)}\n{fcode('$ '+cmd)}\n"
    cmd_str = f'printf "{print_str}" && {cmd}'
    with cd(repository):
        return subprocess.run(cmd_str, capture_output=True, shell=True)
