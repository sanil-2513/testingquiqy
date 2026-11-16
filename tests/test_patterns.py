import pytest
from goodbite.auth_menu.menu_factory import MenuItemFactory
from goodbite.auth_menu.menu_proxy import MenuManagementProxy
from goodbite.cart_customization.cart import ShoppingCart
from goodbite.cart_customization.commands import AddItemCommand, RemoveItemCommand, ChangeQuantityCommand, CartInvoker
from goodbite.cart_customization.customization import build_customized_food
from goodbite.cart_customization.meal_builder import MealComboBuilder
from goodbite.checkout_payment.discounts import get_discount_strategy
from goodbite.checkout_payment.checkout_facade import CheckoutFacade
from goodbite.orders_delivery.order import Order
from goodbite.orders_delivery.order_states import PlacedState, PreparingState, OutForDeliveryState, DeliveredState
from goodbite.orders_delivery.observers import NotificationCenter, OrderObserver

def test_factory_and_proxy():
    item=MenuItemFactory.create("main","Burger","Fresh burger",100)
    assert item.price==100
    with pytest.raises(ValueError): MenuItemFactory.create("invalid","X","Y",1)
    class DB:
        def insert_menu_item(self,item): return 7
        def delete_menu_item(self,item_id): self.deleted=item_id
    proxy=MenuManagementProxy(DB())
    with pytest.raises(PermissionError): proxy.add_item(item,None)
    assert proxy.add_item(item,{"role":"admin"})==7

def test_cart_command_operations():
    cart=ShoppingCart(); invoker=CartInvoker()
    item={"line_id":"x","name":"Burger","price":100,"quantity":1}
    add=invoker.execute(AddItemCommand(cart,item)); assert cart.total==100
    invoker.execute(ChangeQuantityCommand(cart,"x",1)); assert cart.count==2
    remove=invoker.execute(RemoveItemCommand(cart,"x")); assert cart.count==0
    remove.undo(); assert cart.count==2
    add.undo(); assert cart.count==0

def test_decorator_addons_and_builder():
    food=build_customized_food({"name":"Burger","price":100},["cheese","patty"])
    assert food.get_cost()==165
    assert "Extra cheese" in food.get_description()
    combo=(MealComboBuilder().set_name("Lunch").add_main({"category":"main","name":"Burger","price":100})
           .add_side({"category":"side","name":"Fries","price":50})
           .add_drink({"category":"drink","name":"Tea","price":20}).build())
    assert combo["price"]==170

def test_discount_and_checkout_facade():
    assert get_discount_strategy("percentage").calculate(200)==20
    receipt=CheckoutFacade().checkout("Sam",200,"flat","upi")
    assert receipt["final_total"]==150 and receipt["success"]

def test_order_state_pattern():
    order=Order(1,"Sam","Burger","Goa")
    assert order.status=="Placed"
    order.advance(); assert order.status=="Preparing"
    order.advance(); assert order.status=="Out for delivery"
    order.advance(); assert order.status=="Delivered"
    with pytest.raises(ValueError): order.advance()

def test_observer_pattern():
    class RecordingObserver(OrderObserver):
        def __init__(self): self.messages=[]
        def update(self,order,message): self.messages.append(message)
    center=NotificationCenter(); observer=RecordingObserver(); center.subscribe(observer)
    order=Order(1,"Sam","Burger","Goa"); center.notify(order,"Order placed")
    assert observer.messages==["Order placed"]
    center.unsubscribe(observer); center.notify(order,"Next")
    assert len(observer.messages)==1
