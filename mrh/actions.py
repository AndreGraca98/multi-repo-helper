# import os
# import subprocess
# from pathlib import Path

# from mrh.colors import fcode, fname
# from mrh.commands import FREE_CMDS, GIT_CMDS, VENV_CMDS


# class cd:
#     """Context manager for changing the current working directory"""

#     def __init__(self, path: str | Path):
#         self.path = Path(path).resolve()
#         assert self.path.is_dir()
#         self.cwd = Path.cwd()

#     def __enter__(self):
#         os.chdir(self.path)

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         os.chdir(self.cwd)


# def run_cmd(repo: Path, cmd: str):
#     print_str = f"{fname(repo.name)}\n{fcode('$ '+cmd)}\n"
#     cmd_str = f'printf "{print_str}" && {cmd}'
#     with cd(repo):
#         return subprocess.run(cmd_str, capture_output=True, shell=True)


# # Action/Command classes
# class Action:
#     """Action class for executing commands on a repo or top level directory"""

#     class Level:
#         TOP = "top"
#         REPO = "repo"

#     level = NotImplemented  # Top level or repo level action

#     def __init__(self, action: str, **kwargs) -> None:
#         self.action = action
#         self.kwargs = kwargs

#     @property
#     def cmd(self) -> str:
#         raise NotImplementedError

#     def __call__(self, repo: Path) -> subprocess.CompletedProcess:
#         print(f"Current repo: {fname(repo.name)} ")
#         return run_cmd(repo, self.cmd)

#     def __str__(self) -> str:
#         return self.cmd

#     def __repr__(self) -> str:
#         kwargs = ", ".join(f"{k}={v}" for k, v in self.kwargs.items())
#         if kwargs:
#             kwargs = ", " + kwargs
#         return (
#             # f"Action level: {self.level} => "
#             f"{self.__class__.__name__}({self.action}{kwargs})"
#         )


# class Git(Action):
#     level = Action.Level.REPO

#     @property
#     def cmd(self) -> str:
#         return GIT_CMDS[self.action].format(**self.kwargs)


# class Venv(Action):
#     level = Action.Level.REPO

#     @property
#     def cmd(self) -> str:
#         return VENV_CMDS[self.action].format(**self.kwargs)


# class Free(Action):
#     level = Action.Level.REPO

#     @property
#     def cmd(self) -> str:
#         return FREE_CMDS[self.action].format(**self.kwargs)
