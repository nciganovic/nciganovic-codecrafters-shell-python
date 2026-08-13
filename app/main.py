import readline
import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings

from .commands import CommandExecutor
from .completer import complete_command
from .parser import InputParser

kb = KeyBindings()

readline.set_completer(complete_command)
readline.parse_and_bind("tab: complete")
readline.set_completer_delims(" \t\n;")


@kb.add("up")
def previous_history(event):
    buf = event.app.current_buffer
    buf.text = "ciga piga"
    buf.cursor_position = len(buf.text)

@kb.add("down")
def next_history(event):
    buf = event.app.current_buffer
    buf.text = ""
    buf.cursor_position = 0

session = PromptSession(key_bindings=kb)


def main():
    executor = CommandExecutor()
    while True:
        try:
            user_input_str = session.prompt("$ ")
        except EOFError:
            break
        if not user_input_str:
            continue

        parse_result = InputParser(user_input_str).parse()
        executor.execute(parse_result)
        readline.add_history(user_input_str)


if __name__ == "__main__":
    main()
