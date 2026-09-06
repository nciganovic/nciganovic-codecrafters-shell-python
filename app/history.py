import os
from .consts import WRITE_MODE, APPEND_MODE, NEW_LINE

class History:
    def __init__(self):
        self._items = []
        self._pointer = 0
        self._last_append_pos = 0 

        env = os.environ.copy()
        if "HISTFILE" in env:
            self.read_from_file(os.environ["HISTFILE"])
        

    def add_item(self, item: str) -> None:
        self._items.append(item)
        self._pointer = len(self._items) - 1

    def __getitem__(self, item):
        return self._items[item]

    def __len__(self):
        return len(self._items)

    def get_previous(self) -> str:
        if not self._items:
            return ""
        item = self._items[self._pointer]
        self._pointer = max(self._pointer - 1, 0)
        return item

    def get_next(self) -> str:
        if not self._items:
            return ""
        self._pointer += 1
        if self._pointer >= len(self._items):
            self._pointer = len(self._items) - 1
            return ""
        return self._items[self._pointer]

    def clear(self) -> None:
        self._items.clear()
        self._pointer = 0

    def read_from_file(self, file_path: str):
        try:
            with open(file_path, "r") as f:
                for line in f:
                    line = line.rstrip("\n")
                    if line:
                        self.add_item(line)
        except FileNotFoundError:
            print(f"history: {file_path}: No such file or directory")

    def write_to_file(self, file_name: str, is_append: bool):
        mode = APPEND_MODE if is_append else WRITE_MODE
        items = self._items if mode is WRITE_MODE else self._items[self._last_append_pos:]

        self._last_append_pos = len(self._items)
        with open(file_name, mode) as file:
            file.write('\n'.join(items) + '\n')
