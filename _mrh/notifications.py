import platform
import subprocess

from .actions import Action


def notify(action: Action):
    text = f"""MRH finished running:
    \u2022\t {action._command} > {action._subcommand} > {action}
"""

    if platform.system() == "Darwin":
        notify_macos(text)
    elif platform.system() == "Linux":
        notify_linux(text)
    elif platform.system() == "Windows":
        notify_windows(text)
    else:
        raise NotImplementedError


def notify_macos(text: str):
    # # Use macos voice to notify when the actions are finished
    # subprocess.run("say Finished", shell=True)

    # Use macos dialog to notify when the actions are finished
    app = "System Events"
    button_text = "OK"
    title = "Multi Repo Helper"
    osascript = (
        f'tell application "{app}" to display '
        f'dialog "{text}" buttons {{"{button_text}"}} '
        f'default button 1 with title "{title}"'
    )
    cmd = f"osascript -e '{osascript}' >/dev/null"
    subprocess.run(cmd, shell=True)


def notify_linux(text: str):
    raise NotImplementedError


def notify_windows(text: str):
    raise NotImplementedError
