__all__ = [
    "cs",
    "ftitle",
    "funderline",
    "fstrike",
    "fname",
    "fcode",
    "ferror",
    "fsuccess",
    "fhelp",
]


# Console pretty printing
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


ftitle = cs(cs.BOLD, cs.UNDERLINE, cs.YELLOW)
funderline = cs(cs.UNDERLINE)
fstrike = cs(cs.STRIKE)
fname = cs(cs.BOLD, cs.UNDERLINE, cs.MUTE, cs.BBLUE)
fcode = cs(cs.ITALIC, cs.MUTE, cs.GREEN)
ferror = cs(cs.BOLD, cs.BLINK, cs.RED)
fsuccess = cs(cs.BOLD, cs.GREEN)
fhelp = cs(cs.YELLOW, cs.MUTE)

#
fmagenta = cs(cs.MAGENTA, cs.BOLD)
fred = cs(cs.RED)
fyellow = cs(cs.YELLOW)
fblue = cs(cs.BLUE)
fgreen = cs(cs.GREEN)
