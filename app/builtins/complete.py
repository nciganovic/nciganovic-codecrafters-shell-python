class Complete:
    def __init__(self):
        self.items = {} 

    def add_item(self, path: str, command: str):
        self.items[command] = path

    def get_item(self, command: str):
        if command not in self.items:
            return None
        return self.items[command]
