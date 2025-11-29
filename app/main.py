import sys


def main():
    # TODO: Uncomment the code below to pass the first stage
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        elements: List[str] = user_input.split(' ')
        command = elements[0]

        if(command == 'echo'):
            print(user_input[5:])
        elif(command == 'exit'):
            sys.exit()
        else:
            print(f'{command}: command not found')


if __name__ == "__main__":
    main()
