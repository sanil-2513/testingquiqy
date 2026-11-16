from abc import ABC, abstractmethod

class CartCommand(ABC):
    @abstractmethod
    def execute(self): ...
    @abstractmethod
    def undo(self): ...

class AddItemCommand(CartCommand):
    def __init__(self, cart, item): self.cart, self.item = cart, dict(item)
    def execute(self): self.cart.add(self.item)
    def undo(self): self.cart.remove(self.item["line_id"])

class RemoveItemCommand(CartCommand):
    def __init__(self, cart, line_id):
        self.cart, self.line_id, self.removed_item = cart, line_id, None
    def execute(self):
        item = self.cart.find(self.line_id)
        self.removed_item = dict(item) if item else None
        self.cart.remove(self.line_id)
    def undo(self):
        if self.removed_item: self.cart.add(self.removed_item)

class ChangeQuantityCommand(CartCommand):
    def __init__(self, cart, line_id, amount): self.cart, self.line_id, self.amount = cart, line_id, amount
    def execute(self): self.cart.change_quantity(self.line_id, self.amount)
    def undo(self): self.cart.change_quantity(self.line_id, -self.amount)

class CartInvoker:
    def execute(self, command):
        command.execute()
        return command
