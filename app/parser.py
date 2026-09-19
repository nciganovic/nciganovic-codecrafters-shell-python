from dataclasses import dataclass
from enum import Enum
from typing import Literal

from .builtins.declare import Declare
from .consts import *


class StdType(str, Enum):
    stdout = "stdout"
    stderr = "stderr"


@dataclass
class InputParseResult:
    command: str
    args: list[str]
    file_to_write: str | None
    std_type: str
    append: bool


class InputParser:
    def __init__(self, user_input_str: str, declare: Declare):
        self._raw_input = user_input_str.strip()
        self._declare = declare

    def parse(self) -> InputParseResult:
        tokens: list[str] = self._convert_input_to_list(self._raw_input)
        file_to_write: str | None = self._get_file_to_write(tokens)
        std_type = StdType.stdout
        append = False
        if file_to_write is not None:
            append = tokens[-2] in STDOUT_APPEND_CMDS
            std_type = self._get_std_type(tokens[-2])
            tokens = tokens[:-2]
        return InputParseResult(
            command=tokens[0],
            args=tokens[1:],
            file_to_write=file_to_write,
            std_type=std_type,
            append=append,
        )

    def _is_writing_to_file(self, args: list[str]) -> bool:
        return len(args) > 2 and args[-2] in STDOUT_CMDS

    def _get_file_to_write(self, args: list[str]) -> str | None:
        if self._is_writing_to_file(args):
            return args[-1]
        return None

    def _get_std_type(self, type: str) -> Literal['stderr', 'stdout']:
        return (
            StdType.stderr.value
            if type == "2>" or type == "2>>"
            else StdType.stdout.value
        )

    def _convert_input_to_list(self, str_input: str) -> list[str]:
        total_args = []
        current_arg = EMPTY
        is_quote_started = False
        current_quote = None
        is_escaping = False

        for char in str_input:
            if is_escaping:
                current_arg += char
                is_escaping = False
                continue

            if char == BACKSLASH and current_quote is not SINGLE_QUOTES:
                is_escaping = True
                continue
            elif self._is_any_quote(char) and (not is_quote_started or char == current_quote):
                current_quote = char
                is_quote_started = not is_quote_started
            elif char == SPACE:
                if is_quote_started:
                    current_arg += char
                elif current_arg != EMPTY:
                    current_arg = self._convert_to_declare_variable(current_arg)
                    if current_arg != '':
                        total_args.append(current_arg)
                    current_arg = EMPTY
            else:
                current_arg += char

        current_arg = self._convert_to_declare_variable(current_arg)
        if current_arg != '':
            total_args.append(current_arg)

        return total_args

    def _is_any_quote(self, char: str) -> bool:
        return char == SINGLE_QUOTES or char == DOUBLE_QUOTES

    def _convert_to_declare_variable(self, arg: str) -> str:
        start_var_idx = 0
        while True:
            start_var_idx = arg.find("$")
            if start_var_idx == -1:
                return arg
            has_bracket = False
            str_extract_index = start_var_idx + 1
            end_extract_index = len(arg)
            if str_extract_index >= end_extract_index:
                return arg
            if arg[start_var_idx + 1] == '{':
                str_extract_index += 1
                end_extract_index = start_var_idx + arg[start_var_idx:].find('}') 
                has_bracket = True

            var_key = arg[str_extract_index:end_extract_index]
            var_value = self._declare.get_item(var_key)

            if has_bracket:
                end_extract_index += 1

            replace_str = var_value if var_value is not None else ''            
            arg = arg.replace(arg[start_var_idx:end_extract_index], replace_str)
