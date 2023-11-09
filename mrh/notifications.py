import platform
import subprocess


def notify(actions):
    actions_str = "\n".join(map(lambda a: f"\u2022\t{a}", actions))

    if platform.system() == "Darwin":
        notify_macos(actions_str)
    elif platform.system() == "Linux":
        notify_linux(actions_str)
    elif platform.system() == "Windows":
        notify_windows(actions_str)
    else:
        raise NotImplementedError


def notify_macos(actions_str: str):
    # # Use macos voice to notify when the actions are finished
    # subprocess.run("say Finished", shell=True)

    # Use macos dialog to notify when the actions are finished
    app = "System Events"
    button_text = "OK"
    title = "MRH"
    text = f"Multi repo helper finished running actions:\n{actions_str}"
    osascript = (
        f'tell application "{app}" to display '
        f'dialog "{text}" buttons {{"{button_text}"}} '
        f'default button 1 with title "{title}"'
    )
    cmd = f"osascript -e '{osascript}' >/dev/null"
    subprocess.run(cmd, shell=True)


def notify_linux(actions_str: str):
    raise NotImplementedError


def notify_windows(actions_str: str):
    raise NotImplementedError
