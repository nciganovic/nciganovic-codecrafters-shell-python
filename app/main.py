import readline

from .builtins.complete import Complete
from .builtins.declare import Declare
from .builtins.history import History
from .builtins.jobs import Jobs
from .commands import CommandExecutor
from .completer import make_completer
from .parser import InputParser

readline.parse_and_bind("tab: complete")
readline.set_completer_delims(" \t\n;")
readline.set_auto_history(True)


def main():
    history = History()
    jobs = Jobs()
    complete = Complete()
    declare = Declare()

    readline.set_completer(make_completer(complete))
    executor = CommandExecutor(history, readline, jobs, complete, declare)

    while True:
        try:
            user_input_str = input("$ ")
        except EOFError:
            break
        if not user_input_str:
            continue

        history.add_item(user_input_str)
        parse_result = InputParser(user_input_str, declare).parse()
        executor.execute(parse_result)


if __name__ == "__main__":
    main()
