import sys

built_in_commands = ['echo', 'exit', 'type']

def main():
    # TODO: Uncomment the code below to pass the first stage
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
                    print(f'{a} not found')
        elif(command == 'exit'):
            sys.exit()
        else:
            print(f'{command}: command not found')


if __name__ == "__main__":
    main()
