from abc import ABC, abstractmethod

class FoodComponent(ABC):
    @abstractmethod
    def get_description(self): ...
    @abstractmethod
    def get_cost(self): ...

class BasicFood(FoodComponent):
    def __init__(self, name, price): self.name, self.price = name, float(price)
    def get_description(self): return self.name
    def get_cost(self): return self.price

class FoodAddonDecorator(FoodComponent):
    def __init__(self, food): self.food = food
    def get_description(self): return self.food.get_description()
    def get_cost(self): return self.food.get_cost()

class ExtraCheese(FoodAddonDecorator):
    def get_description(self): return self.food.get_description() + ", Extra cheese"
    def get_cost(self): return self.food.get_cost() + 25
class ExtraPatty(FoodAddonDecorator):
    def get_description(self): return self.food.get_description() + ", Extra patty"
    def get_cost(self): return self.food.get_cost() + 40
class ExtraToppings(FoodAddonDecorator):
    def get_description(self): return self.food.get_description() + ", Extra toppings"
    def get_cost(self): return self.food.get_cost() + 20
class Jalapenos(FoodAddonDecorator):
    def get_description(self): return self.food.get_description() + ", Jalapeños"
    def get_cost(self): return self.food.get_cost() + 15
class SpecialSauce(FoodAddonDecorator):
    def get_description(self): return self.food.get_description() + ", Special sauce"
    def get_cost(self): return self.food.get_cost() + 10
