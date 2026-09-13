import os

from ..consts import APPEND_MODE, WRITE_MODE


class History:
    def __init__(self):
        self._items = []
        self._pointer = 0
        self._last_append_pos = 0 

        self.load_from_env_file() 
        

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
        if file_path is None or file_path == "":
            return
        try:
            with open(file_path, "r") as f:
                for line in f:
                    line = line.rstrip("\n")
                    if line:
                        self.add_item(line)
        except FileNotFoundError:
            print(f"history: {file_path}: No such file or directory")

    def write_to_file(self, file_name: str, is_append: bool):
        if file_name is None or file_name == "":
            return
        mode = APPEND_MODE if is_append else WRITE_MODE
        items = self._items if mode is WRITE_MODE else self._items[self._last_append_pos:]

        self._last_append_pos = len(self._items)
        with open(file_name, mode) as file:
            file.write('\n'.join(items) + '\n')

    def  _get_history_env_file(self):
        env = os.environ.copy()
        return env["HISTFILE"] if "HISTFILE" in env else None        

    def load_from_env_file(self):
        file = self._get_history_env_file()
        self.read_from_file(file)

    def write_to_env_file(self):
        file = self._get_history_env_file()
        self.write_to_file(file, False)