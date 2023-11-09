from multiprocessing import Pool
from pathlib import Path

from mrh.actions import Action, get_filtered_dirs
from mrh.colors import cs
from mrh.configuration import Configuration
from mrh.notifications import notify
from mrh.parser import get_parser

ferror = cs(cs.BOLD, cs.BLINK, cs.RED)
fsuccess = cs(cs.BOLD, cs.GREEN)
funderline = cs(cs.UNDERLINE)
fstrike = cs(cs.STRIKE)
fcode = cs(cs.ITALIC, cs.MUTE, cs.GREEN)


def multi_action(
    action: Action,
    repositories: list[Path],
    verbose: bool,
    pool_size: int = 10,
):
    print(f"Running {fcode(str(action))} in {len(repositories)} repositories...")
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
    args = parser.parse_args()

    argsd = dict(args._get_kwargs())
    cfg: Configuration = argsd.pop("config")

    action = Action(**argsd)

    filtered_repositories = get_filtered_dirs(Path.cwd().resolve(), cfg.filter)

    multi_action(action, filtered_repositories, cfg.verbose, cfg.pool_size)

    if cfg.no_notify:
        return

    notify(action)
