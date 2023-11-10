from multiprocessing import Pool
from pathlib import Path

from .actions import Action
from .configuration import Configuration
from .logger import get_logger
from .notifications import notify
from .parser import get_parser
from .tabcompletion import tabcomplete
from .terminal import cs

__all__ = ["main"]

_log = get_logger(__name__)

ferror = cs(cs.BOLD, cs.BLINK, cs.RED)
fsuccess = cs(cs.BOLD, cs.GREEN)
funderline = cs(cs.UNDERLINE)
fstrike = cs(cs.STRIKE)
fcode = cs(cs.ITALIC, cs.MUTE, cs.GREEN)


def filter_dirs(directory: Path, filter_str: str) -> set[Path]:
    """Get all directories in a given directory that match a
    filter string and are git repositories"""
    directory = directory.resolve()
    return set(filter(lambda p: (p / ".git").is_dir(), directory.glob(filter_str)))


def get_filtered_dirs(directory: Path, filter_strs: list[str]) -> list[Path]:
    total_filtered: set[Path] = set()
    for filter_str in filter_strs:
        filtered = filter_dirs(directory, filter_str)
        total_filtered.update(filtered)
    return sorted(total_filtered)


def multi_action(
    action: Action,
    repositories: list[Path],
    verbose: bool,
    pool_size: int = 10,
):
    _log.info(f"Running {fcode(str(action))} in {len(repositories)} repositories...")
    with Pool(pool_size) as p:
        results = p.map(action, repositories)
        print("=" * 100)
        for r in results:
            if not verbose and r.returncode == 0:
                continue

            txt = ""
            txt += ferror("[FAILED]") if r.returncode else fsuccess("[SUCCESS]")
            txt += f"\n{funderline('Stdout')}: {r.stdout.decode()}"
            txt += f"\n{funderline('Stderr')}: {r.stderr.decode()}\n"
            txt += fstrike("=" * 100)

            print(txt)


def main():
    parser = get_parser()
    tabcomplete(parser)  # if tabcomplete is called, it will exit the program

    args = parser.parse_args()
    argsd = dict(args._get_kwargs())
    cfg: Configuration = argsd.pop("config")

    action = Action(**argsd)
    filtered_repositories = get_filtered_dirs(Path.cwd().resolve(), cfg.filter)
    multi_action(action, filtered_repositories, cfg.verbose, cfg.pool_size)

    if cfg.no_notify:
        return
    notify(action)
