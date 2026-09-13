import os
import readline
import shlex
import subprocess
import sys

from .consts import SPACE

is_complete_state = False


def make_completer(complete):
    """Create a readline completer that can run registered -C scripts."""

    script_matches: list[str] = []

    def complete_command(text, state):
        global is_complete_state
        nonlocal script_matches

        if state != 0:
            # readline asks for the Nth match (state = 1, 2, ...)
            if state - 1 < len(script_matches):
                return script_matches[state - 1] + SPACE
            return None

        script_matches = []

        full_line = readline.get_line_buffer()
        begidx = readline.get_begidx()
        line_before = full_line[:begidx]

        try:
            args = shlex.split(line_before, posix=True)
        except ValueError:
            args = line_before.strip().split()

        # Argument completion for a registered command 
        if args:
            script_path = complete.get_item(args[0])
            if script_path is not None:
                script_matches = _run_script(script_path, text)
                if script_matches:
                    return script_matches[0] + SPACE  
                return None

        if not args:
            # Completing the command name itself
            builtins = ["echo", "exit", "type", "pwd", "cd", "history", "jobs", "complete"]
            for option in builtins:
                if option.startswith(text):
                    return option + SPACE

            suggestions = _get_suggestions(text)

            if not suggestions:
                return None

            if len(suggestions) == 1:
                is_complete_state = False
                return suggestions[0] + SPACE

            common_prefix = os.path.commonprefix(suggestions)
            if len(common_prefix) > len(text):
                is_complete_state = False
                return common_prefix

            if not is_complete_state:
                is_complete_state = True
                sys.stdout.write("\07")
                sys.stdout.flush()
                return None
            else:
                is_complete_state = False
                output = "  ".join(sorted(suggestions))
                print("\n" + output)
                sys.stdout.write("$ " + readline.get_line_buffer())
                sys.stdout.flush()
                return None
        else:
            # Completing file paths as command arguments
            suggestions = _get_file_suggestion(text)

            if len(suggestions) == 1:
                if os.path.isdir(suggestions[0]):
                    return suggestions[0]
                return suggestions[0] + SPACE
            else:
                common_prefix = os.path.commonprefix(suggestions)
                if len(common_prefix) > len(text):
                    is_complete_state = False
                    return common_prefix

                if not is_complete_state:
                    is_complete_state = True
                    sys.stdout.write("\07")
                    sys.stdout.flush()
                    return None
                else:
                    is_complete_state = False
                    output = "  ".join(sorted(suggestions))
                    print("\n" + output)
                    sys.stdout.write("$ " + readline.get_line_buffer())
                    sys.stdout.flush()
                    return None

    return complete_command


def _run_script(script_path: str, text: str) -> list[str]:
    try:
        result = subprocess.run(
            [script_path, text],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return []

    matches = []
    for line in result.stdout.splitlines():
        line = line.rstrip("\n")
        if line.startswith(text):
            matches.append(line)
    return matches


def _get_file_suggestion(text: str) -> list[str]:
    original_path = os.getcwd()
    suggestions = []
    extra_path = ""

    if "/" in text:
        text_list = text.split("/")
        extra_path = "/".join(text_list[:-1])
        text = text_list[-1]

    for f in os.listdir(original_path + "/" + extra_path):
        full_suggest = f if extra_path == "" else extra_path + "/" + f

        if f.startswith(text) or text == "":
            if os.path.isdir(original_path + "/" + full_suggest):
                full_suggest += "/"
            suggestions.append(full_suggest)

    return suggestions


def _get_suggestions(arg: str) -> list[str]:
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
