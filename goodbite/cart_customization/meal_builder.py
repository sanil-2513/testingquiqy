class MealComboBuilder:
    """Builder: assembles a combo from one main, one side and one drink."""
    def __init__(self):
        self._name, self._items, self._price = "Meal Combo", [], 0.0
    def set_name(self, name):
        if not name or not name.strip(): raise ValueError("Combo name cannot be empty.")
        self._name = name.strip(); return self
    def add_main(self, item): self._add_item(item, "main"); return self
    def add_side(self, item): self._add_item(item, "side"); return self
    def add_drink(self, item): self._add_item(item, "drink"); return self
    def _add_item(self, item, category):
        if item.get("category") != category: raise ValueError(f"Choose a {category} item.")
        self._items.append(item["name"]); self._price += float(item["price"])
    def build(self):
        if len(self._items) != 3: raise ValueError("A combo needs one main, one side and one drink.")
        return {"name": self._name, "items": list(self._items), "price": round(self._price, 2)}
