class Complete:
    def __init__(self):
        self.items: dict[str, str] = {} 

    def add_item(self, path: str, command: str):
        self.items[command] = path

    def get_item(self, command: str):
        if command not in self.items:
            return None
        return self.items[command]

    def remove_item(self, command: str):
        if command in self.items:
            del self.items[command]
