import sys
import os 
import subprocess

DOUBLE_QUOTES = '"'
SINGLE_QUOTES = "'"
SPACE = ' '
EMPTY = ''
BACKSLASH = '\\'
NEW_LINE = '\n'
STDOUT_CMDS = ['1>', '>']

built_in_commands = ['echo', 'exit', 'type', 'pwd', 'cd']

def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        parsed_command_with_params = convert_input_to_arr(user_input.strip())        
        file_to_write: str | None = get_file_to_write(parsed_command_with_params)
        if file_to_write is not None:
            parsed_command_with_params = parsed_command_with_params[:-2]
        command = parsed_command_with_params[0]


        if(command == 'echo'):
            result = ' '.join(parsed_command_with_params[1:])
            output_result(file_to_write, result)
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
                output_result(file_to_write, subprocess_result.stdout)
                if subprocess_result.stderr != '':
                    output_result(None, subprocess_result.stderr)
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

def output_result(file_to_write: str | None, cmd_result):
    if file_to_write is not None:
        write_to_file(file_to_write, cmd_result)
    else:
        if cmd_result[-1] == NEW_LINE:
            print(cmd_result, end="")
        else: 
            print(cmd_result)

def is_writing_to_file(args: list[str]):
    return len(args) > 2 and args[-2] in STDOUT_CMDS

def write_to_file(file_name: str, content: str):
    with open(file_name, "w+") as file:
        file.write(content)

def get_file_to_write(args: list[str])-> str | None:
    if is_writing_to_file(args):
        return args[-1]
    return None

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
