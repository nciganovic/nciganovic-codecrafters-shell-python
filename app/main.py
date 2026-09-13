import readline

from .builtins.complete import Complete
from .builtins.history import History
from .builtins.jobs import Jobs
from .commands import CommandExecutor
from .completer import complete_command
from .parser import InputParser

readline.set_completer(complete_command)
readline.parse_and_bind("tab: complete")
readline.set_completer_delims(" \t\n;")
readline.set_auto_history(True)


def main():
    history = History()
    jobs = Jobs()
    complete = Complete()
    executor = CommandExecutor(history, readline, jobs, complete)

    while True:
        try:
            user_input_str = input("$ ")
        except EOFError:
            break
        if not user_input_str:
            continue

        history.add_item(user_input_str)
        parse_result = InputParser(user_input_str).parse()
        executor.execute(parse_result)


if __name__ == "__main__":
    main()
