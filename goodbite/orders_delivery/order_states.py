from abc import ABC, abstractmethod
class OrderState(ABC):
    name="Unknown"
    @abstractmethod
    def advance(self,order): ...
    def cancel(self,order): raise ValueError(f"An order in '{self.name}' cannot be cancelled.")
class PlacedState(OrderState):
    name="Placed"
    def advance(self,order): order.state=PreparingState()
    def cancel(self,order): order.state=CancelledState()
class PreparingState(OrderState):
    name="Preparing"
    def advance(self,order): order.state=OutForDeliveryState()
    def cancel(self,order): order.state=CancelledState()
class OutForDeliveryState(OrderState):
    name="Out for delivery"
    def advance(self,order): order.state=DeliveredState()
class DeliveredState(OrderState):
    name="Delivered"
    def advance(self,order): raise ValueError("Already delivered.")
class CancelledState(OrderState):
    name="Cancelled"
    def advance(self,order): raise ValueError("Cancelled orders cannot advance.")
    def cancel(self,order): raise ValueError("Already cancelled.")
STATE_CLASSES={c.name:c for c in [PlacedState,PreparingState,OutForDeliveryState,DeliveredState,CancelledState]}
