class Declare:
    def __init__(self):
        self.items: dict[str, str] = {} 

    def add_item(self, name: str, value: str):
        self.items[name] = value

    def get_item(self, name: str):
        if name not in self.items:
            return None
        return self.items[name]

    def remove_item(self, name: str):
        if name in self.items:
            del self.items[name]
