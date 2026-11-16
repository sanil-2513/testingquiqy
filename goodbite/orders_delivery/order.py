from dataclasses import dataclass, field
from datetime import datetime
from .order_states import PlacedState
@dataclass
class Order:
    id:int
    customer:str
    item:str
    address:str
    state:object=field(default_factory=PlacedState)
    created_at:str=field(default_factory=lambda:datetime.now().strftime("%d-%m-%Y %H:%M"))
    @property
    def status(self): return self.state.name
    def advance(self): self.state.advance(self)
    def cancel(self): self.state.cancel(self)
