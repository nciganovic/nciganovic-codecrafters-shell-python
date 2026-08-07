import readline
import sys

from .commands import CommandExecutor
from .completer import complete_command
from .parser import InputParser

readline.set_completer(complete_command)
readline.parse_and_bind("tab: complete")
readline.set_completer_delims(" \t\n;")


def main():
    executor = CommandExecutor()
    while True:
        sys.stdout.write("$ ")
        user_input_str = input()
        parse_result = InputParser(user_input_str).parse()
        executor.execute(parse_result)

if __name__ == "__main__":
    main()
