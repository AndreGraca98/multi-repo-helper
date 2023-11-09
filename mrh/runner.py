from pathlib import Path

from mrh.actions import Action
from mrh.notifications import notify
from mrh.parser import get_parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    print(args)
    argsd = dict(args._get_kwargs())
    cfg = argsd.pop("config")
    print(cfg)
    print(argsd)
    action = Action(**argsd)
    print(action)
    result = action.run(Path.cwd())
    print(result)

    if cfg.no_notify:
        return

    notify(action)
