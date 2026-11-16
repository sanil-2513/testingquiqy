from abc import ABC, abstractmethod
class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, subtotal): ...
class NoDiscount(DiscountStrategy):
    def calculate(self, subtotal): return 0.0
class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage):
        if not 0 <= percentage <= 100: raise ValueError("Invalid percentage.")
        self.percentage=percentage
    def calculate(self, subtotal): return round(subtotal*self.percentage/100,2)
class FlatDiscount(DiscountStrategy):
    def __init__(self, amount):
        if amount<0: raise ValueError("Discount cannot be negative.")
        self.amount=amount
    def calculate(self, subtotal): return round(min(subtotal,self.amount),2)
DISCOUNT_OPTIONS={"none":"No discount","percentage":"10% discount","flat":"₹50 off"}
def get_discount_strategy(kind):
    choices={"none":NoDiscount(),"percentage":PercentageDiscount(10),"flat":FlatDiscount(50)}
    if kind not in choices: raise ValueError("Select a valid discount.")
    return choices[kind]
