import sys
import os 
import subprocess
from enum import Enum

DOUBLE_QUOTES = '"'
SINGLE_QUOTES = "'"
SPACE = ' '
EMPTY = ''
BACKSLASH = '\\'
NEW_LINE = '\n'
STDOUT_CMDS = ['>', '>>', '1>>', '1>', '2>']

built_in_commands = ['echo', 'exit', 'type', 'pwd', 'cd']

class StdType(str, Enum):
    stdout = 'stdout'
    stderr = 'stderr'

def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        parsed_command_with_params = convert_input_to_arr(user_input.strip())        
        file_to_write: str | None = get_file_to_write(parsed_command_with_params)
        std_type = StdType.stdout
        append = False
        if file_to_write is not None:
            append = parsed_command_with_params[-2] == '>>' or parsed_command_with_params[-2] == '1>>'
            std_type = get_std_type(parsed_command_with_params[-2])
            parsed_command_with_params = parsed_command_with_params[:-2]
        command = parsed_command_with_params[0]

        if(command == 'echo'):
            result = ' '.join(parsed_command_with_params[1:])
            output_result(file_to_write, std_type, result, "", append)
        elif(command == 'type'):
            args = parsed_command_with_params[1:]
            for a in args:
                if a in built_in_commands:
                    print(f'{a} is a shell builtin')
                else:
                    full_path = get_execute_path(a)
                    if full_path is not None:
                        print(f'{a} is {full_path}')
                    else:
                        print(f'{a} not found')
        elif(command == 'exit'):
            sys.exit()
        elif(command == "pwd"):
            print(os.getcwd())
        elif(command == "cd"):
            args = parsed_command_with_params[1:]
            from pathlib import Path
            if len(args) == 0 or args[0] == '~':
                os.chdir(Path.home())
                continue
            if len(args) > 2:
                print("bash: cd: too many arguments")
            
            path = args[0]

            try: 
                os.chdir(path)
            except:
                print(f"cd: {path}: No such file or directory")
        else:
            if get_execute_path(command) is not None:
                subprocess_result = subprocess.run(parsed_command_with_params, capture_output=True, text=True)
                output_result(file_to_write, std_type, subprocess_result.stdout, subprocess_result.stderr, append)
            else:        
                print(f'{command}: command not found')

def get_execute_path(arg: str):
    #Check in PATH
    PATH = os.environ.get("PATH")
    all_paths = PATH.split(os.pathsep)
    for path in all_paths:
        full_path = path + "/" + arg
        if os.path.exists(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return None

def output_result(
    file_to_write: str | None, 
    std_type: StdType, 
    stdout: str,
    stderr: str,
    append: bool
    ):
    if file_to_write is not None:
        output_to_file = stdout if std_type == StdType.stdout else stderr
        output_to_console = stderr if std_type == StdType.stdout else stdout
        write_to_file(file_to_write, output_to_file, append)
        print_res(output_to_console)
    else:
        print_res(stdout)

def print_res(res: str):
    if res == "":
        return
    if res[-1] == NEW_LINE:
        print(res, end="")
    else: 
        print(res)

def is_writing_to_file(args: list[str]):
    return len(args) > 2 and args[-2] in STDOUT_CMDS

def write_to_file(file_name: str, content: str, append: bool):
    mode = 'a+' if append else 'w+' 
    with open(file_name, mode) as file:
        if os.stat(file_name).st_size > 0:
            file.write(NEW_LINE)
        file.write(content)

def get_file_to_write(args: list[str])-> str | None:
    if is_writing_to_file(args):
        return args[-1]
    return None

def get_std_type(type: str)-> StdType:
    return StdType.stderr.value if type == '2>' else StdType.stdout.value

def convert_input_to_arr(str_input):
    total_args = []
    current_arg = EMPTY
    is_quote_started = False
    current_quote = None
    is_escaping = False

    for index, char in enumerate(str_input): 
        if is_escaping:
            current_arg += char
            is_escaping = False
            continue

        if char == BACKSLASH and current_quote is not SINGLE_QUOTES:
            is_escaping = True
            continue
        elif is_any_quote(char) and (not is_quote_started or char == current_quote):            
            current_quote = char
            is_quote_started = not is_quote_started
        elif char == SPACE:
            if is_quote_started:
                current_arg += char
            elif current_arg != EMPTY:
                total_args.append(current_arg)
                current_arg = EMPTY
        else:
            current_arg += char

    total_args.append(current_arg)

    return total_args 

def is_any_quote(char: str)-> bool:
    return char == SINGLE_QUOTES or char == DOUBLE_QUOTES

if __name__ == "__main__":
    main()
