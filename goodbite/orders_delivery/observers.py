from abc import ABC,abstractmethod
from datetime import datetime
class OrderObserver(ABC):
    @abstractmethod
    def update(self,order,message): ...
class NotificationCenter:
    def __init__(self): self._observers=[]
    def subscribe(self,observer):
        if observer not in self._observers: self._observers.append(observer)
    def unsubscribe(self,observer):
        if observer in self._observers: self._observers.remove(observer)
    def notify(self,order,message):
        for observer in list(self._observers): observer.update(order,message)
class EmailNotification(OrderObserver):
    """Email simulation only; configure a real email provider separately."""
    def update(self,order,message): print(f"[EMAIL SIMULATION] {order.customer}: Order #{order.id}: {message}")
class ConsoleNotification(OrderObserver):
    def update(self,order,message): print(f"[NOTIFICATION] Order #{order.id}: {message} ({datetime.now():%H:%M:%S})")
