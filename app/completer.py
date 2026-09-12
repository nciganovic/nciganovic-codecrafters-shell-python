import os
import readline
import sys
import shlex

from .consts import SPACE

is_complete_state = False


def complete_command(text, state):
    """readline completer with custom TAB behavior."""
    global is_complete_state

    if state != 0:
        return None

    full_line = readline.get_line_buffer()                                                                                                                                                 
    begidx = readline.get_begidx()                                                                                                                                                                                    
    line_before = full_line[:begidx]                                                                                                                                                       
                                                                                                                
    try:                                                                                                                                                                                   
        args = shlex.split(line_before, posix=True)                                                                                                                                        
    except ValueError:                                                                                                                                                                     
        args = line_before.strip().split()                                                                                                                                                 
                                                                                                                                                                                              
    arg_len = len(args)

    if arg_len == 0:
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


def _get_file_suggestion(text: str) -> list[str]:
    original_path = os.getcwd()
    suggestions = []
    extra_path = ''
     
    if '/' in text:
        text_list = text.split('/')
        extra_path = '/'.join(text_list[:-1])
        text = text_list[-1]

    for f in os.listdir(original_path + "/" + extra_path):
        full_suggest = f if extra_path == '' else  extra_path + '/' + f
         
        if f.startswith(text) or text == '':
            if os.path.isdir(original_path + '/' + full_suggest):
                full_suggest += '/'
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
