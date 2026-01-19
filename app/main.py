import sys
import os 
import subprocess

built_in_commands = ['echo', 'exit', 'type', 'pwd']

def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        elements: List[str] = user_input.split(' ')
        command = elements[0]
        args:List[str] = elements[1:]

        if(command == 'echo'):
            print(user_input[5:])
        elif(command == 'type'):
            for a in args:
                if a in built_in_commands:
                    print(f'{a} is a shell builtin')
                else:
                    #Check in PATH
                    PATH = os.environ.get("PATH")
                    all_paths = PATH.split(os.pathsep)
                    execute_allowed = False
                    for path in all_paths:
                        full_path = path + "/" + a
                        if os.path.exists(full_path) and os.access(full_path, os.X_OK):
                            print(f'{a} is {full_path}')
                            execute_allowed = True
                            break
                    if not execute_allowed:
                        print(f'{a} not found')
        elif(command == 'exit'):
            sys.exit()
        elif(command == "pwd"):
            print(os.getcwd())
        else:
            #Check in PATH
            PATH = os.environ.get("PATH")
            all_paths = PATH.split(os.pathsep)
            execute_allowed = False
            for path in all_paths:
                full_path = path + "/" + command
                if os.path.exists(full_path) and os.access(full_path, os.X_OK):
                    execute_allowed = True
                    break
            if execute_allowed:
                commands = [command]
                commands.extend(args)
                subprocess.run(commands)
                continue

            print(f'{command}: command not found')

            


if __name__ == "__main__":
    main()
