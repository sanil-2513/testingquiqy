from dataclasses import dataclass

@dataclass
class MenuItem:
    name: str
    description: str
    category: str
    price: float

class MenuItemFactory:
    """Factory Method: creates validated menu items by category."""
    CATEGORIES = ("main", "side", "drink", "dessert")

    @staticmethod
    def create(category, name, description, price):
        if category not in MenuItemFactory.CATEGORIES:
            raise ValueError("Unsupported menu category.")
        if not name.strip() or not description.strip() or float(price) <= 0:
            raise ValueError("Menu item details are invalid.")
        return MenuItem(name.strip(), description.strip(), category, round(float(price), 2))
