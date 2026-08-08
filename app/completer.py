import os
import readline
import sys

from .consts import SPACE

is_complete_state = False


def complete_command(text, state):
    global is_complete_state

    # Only act on first call per TAB press (state 0)
    if state != 0:
        return None

    # Check built-in commands first
    options = ["echo", "exit"]
    for option in options:
        if option.startswith(text):
            return option + SPACE

    suggestions = get_suggestions(text)

    if len(suggestions) == 0:
        return None

    if len(suggestions) == 1:
        # Only one match — autocomplete immediately on any TAB press
        is_complete_state = False
        return suggestions[0] + SPACE

    suggest_by_len = sorted(suggestions, key=len)
    if len(suggest_by_len[0]) != len(suggest_by_len[1]): 
        return suggest_by_len[0]

    if not is_complete_state:
        # First TAB press: just ring bell
        is_complete_state = True
        print("\07", end="", flush=True)
        sorted(suggestions, key=len)
        return None
    else:
        # Second TAB press: show items and restore prompt
        is_complete_state = False
        output = "  ".join(sorted(suggestions))
        print("\n" + output)
        sys.stdout.write("$ " + readline.get_line_buffer())
        sys.stdout.flush()
        return None


def get_suggestions(arg: str):
    items = []
    PATH = os.environ.get("PATH")
    if PATH is None:
        return items
    all_paths = PATH.split(os.pathsep)
    for path in all_paths:
        if not os.path.isdir(path):
            continue
        try:
            files = [
                f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
            ]
        except (PermissionError, OSError):
            continue
        for file in files:
            if file.startswith(arg):
                items.append(file)
    return items
