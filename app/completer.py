import os
import readline
import sys

from .consts import SPACE

is_complete_state = False


def complete_command(text, state):
    """readline completer with custom TAB behavior."""
    global is_complete_state

    # readline calls this repeatedly with state=0,1,2,... for each TAB press.
    # We only compute matches once per TAB press (state 0).
    if state != 0:
        return None

    # Built-in commands first
    builtins = ["echo", "exit", "type", "pwd", "cd", "history"]
    for option in builtins:
        if option.startswith(text):
            return option + SPACE

    suggestions = _get_suggestions(text)

    if not suggestions:
        return None

    if len(suggestions) == 1:
        is_complete_state = False
        return suggestions[0] + SPACE

    # Multiple matches: complete to the longest common prefix first.
    common_prefix = os.path.commonprefix(suggestions)
    if len(common_prefix) > len(text):
        is_complete_state = False
        return common_prefix

    if not is_complete_state:
        # First TAB press with multiple matches and no further common prefix:
        # just ring the bell.
        is_complete_state = True
        sys.stdout.write("\07")
        sys.stdout.flush()
        return None
    else:
        # Second TAB press: show the list and redraw the prompt.
        is_complete_state = False
        output = "  ".join(sorted(suggestions))
        print("\n" + output)
        sys.stdout.write("$ " + readline.get_line_buffer())
        sys.stdout.flush()
        return None


def _get_suggestions(arg: str):
    items = []
    PATH = os.environ.get("PATH")
    if PATH is None:
        return items

    for path in PATH.split(os.pathsep):
        if not os.path.isdir(path):
            continue
        try:
            files = [
                f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
            ]
        except (PermissionError, OSError):
            continue
        for file in files:
            if file.startswith(arg) and file not in items:
                items.append(file)

    return items
