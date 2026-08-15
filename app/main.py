import readline

from .commands import CommandExecutor
from .completer import complete_command
from .history import History
from .parser import InputParser

readline.set_completer(complete_command)
readline.parse_and_bind("tab: complete")
readline.set_completer_delims(" \t\n;")
readline.set_auto_history(True)


def main():
    history = History()
    executor = CommandExecutor(history, readline)

    while True:
        user_input_str = input("$ ")
        if user_input_str is None:
            break
        if not user_input_str:
            continue

        history.add_item(user_input_str)
        parse_result = InputParser(user_input_str).parse()
        executor.execute(parse_result)


if __name__ == "__main__":
    main()
