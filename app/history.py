class History:
    def __init__(self):
        self._items = []
        self._pointer = 0

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
