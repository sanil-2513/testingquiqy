import os, uuid
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from goodbite.database import DatabaseManager
from goodbite.auth_menu.menu_factory import MenuItemFactory
from goodbite.auth_menu.menu_proxy import MenuManagementProxy
from goodbite.cart_customization.cart import ShoppingCart
from goodbite.cart_customization.commands import AddItemCommand, RemoveItemCommand, ChangeQuantityCommand, CartInvoker
from goodbite.cart_customization.customization import ADD_ONS, build_customized_food
from goodbite.cart_customization.meal_builder import MealComboBuilder
from goodbite.checkout_payment.checkout_facade import CheckoutFacade
from goodbite.checkout_payment.discounts import DISCOUNT_OPTIONS
from goodbite.checkout_payment.payment_adapters import PAYMENT_METHODS
from goodbite.orders_delivery.observers import NotificationCenter, EmailNotification, ConsoleNotification
from goodbite.orders_delivery.order_service import OrderService

app=Flask(__name__)
app.secret_key=os.getenv("SECRET_KEY","change-this-development-secret-before-deployment")
db=DatabaseManager()
menu_proxy=MenuManagementProxy(db)
checkout_facade=CheckoutFacade()
cart_invoker=CartInvoker()
notifications=NotificationCenter()
notifications.subscribe(EmailNotification())
notifications.subscribe(ConsoleNotification())
orders=OrderService(db,notifications)

def current_user():
    uid=session.get("user_id")
    return db.get_user_by_id(uid) if uid else None

def login_required(fn):
    @wraps(fn)
    def wrapper(*args,**kwargs):
        if not current_user():
            flash("Please log in to continue.","error")
            return redirect(url_for("login"))
        return fn(*args,**kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args,**kwargs):
        user=current_user()
        if not user or user["role"]!="admin":
            flash("Administrator access is required.","error")
            return redirect(url_for("index"))
        return fn(*args,**kwargs)
    return wrapper

def cart():
    return ShoppingCart.from_list(session.get("cart",[]))

def save_cart(value):
    session["cart"]=value.to_list()
    session.modified=True

@app.before_request
def initialize_database():
    # Safe to call repeatedly; schema and seed data use IF NOT EXISTS / empty checks.
    db.initialize()

@app.get("/")
def index():
    return render_template("index.html",user=current_user(),foods=db.get_menu(),
        cart=cart(),addons=ADD_ONS,orders=orders.get_all_orders(current_user()),
        discount_options=DISCOUNT_OPTIONS,payment_methods=PAYMENT_METHODS)

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form.get("name","").strip()
        email=request.form.get("email","").strip().lower()
        password=request.form.get("password","")
        if not name or "@" not in email or len(password)<8:
            flash("Enter a name, valid email and password of at least 8 characters.","error")
        else:
            try:
                db.create_user(name,email,generate_password_hash(password))
                flash("Account created. Please log in.","success")
                return redirect(url_for("login"))
            except IntegrityError:
                flash("That email is already registered.","error")
        return redirect(url_for("register"))
    return render_template("auth.html",mode="register",user=current_user())

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        user=db.get_user_by_email(request.form.get("email","").strip().lower())
        if not user or not check_password_hash(user["password_hash"],request.form.get("password","")):
            flash("Email or password is incorrect.","error")
            return redirect(url_for("login"))
        session.clear(); session["user_id"]=user["id"]
        flash(f"Welcome, {user['name']}!","success")
        return redirect(url_for("index"))
    return render_template("auth.html",mode="login",user=current_user())

@app.post("/logout")
@login_required
def logout():
    session.clear(); flash("Logged out.","success")
    return redirect(url_for("index"))

@app.post("/cart/add/<int:item_id>")
@login_required
def add_to_cart(item_id):
    food=db.get_menu_item(item_id)
    if not food: flash("Menu item not found.","error"); return redirect(url_for("index"))
    selected=request.form.getlist("addons")
    customized=build_customized_food(food,selected)
    line={"line_id":uuid.uuid4().hex[:12],"menu_id":food["id"],
          "name":customized.get_description(),"price":round(customized.get_cost(),2),"quantity":1}
    c=cart(); cart_invoker.execute(AddItemCommand(c,line)); save_cart(c)
    flash(f"{food['name']} added to your cart.","success")
    return redirect(url_for("index"))

@app.post("/cart/<line_id>/quantity")
@login_required
def change_quantity(line_id):
    try: amount=int(request.form.get("amount","0"))
    except ValueError: amount=0
    if amount not in (-1,1): flash("Invalid quantity change.","error")
    else:
        c=cart(); cart_invoker.execute(ChangeQuantityCommand(c,line_id,amount)); save_cart(c)
    return redirect(url_for("index"))

@app.post("/cart/<line_id>/remove")
@login_required
def remove_from_cart(line_id):
    c=cart(); cart_invoker.execute(RemoveItemCommand(c,line_id)); save_cart(c)
    return redirect(url_for("index"))

@app.post("/cart/clear")
@login_required
def clear_cart():
    session["cart"]=[]; return redirect(url_for("index"))

@app.post("/cart/combo")
@login_required
def add_combo():
    foods={str(f["id"]):f for f in db.get_menu()}
    try:
        main,side,drink=(foods[request.form[k]] for k in ("main","side","drink"))
        combo=(MealComboBuilder().set_name("GoodBite Combo").add_main(main).add_side(side).add_drink(drink).build())
        c=cart()
        c.add({"line_id":uuid.uuid4().hex[:12],"menu_id":None,"name":" + ".join(combo["items"]),
               "price":combo["price"],"quantity":1})
        save_cart(c); flash("Meal combo added.","success")
    except (KeyError,ValueError):
        flash("Choose one valid main, side and drink.","error")
    return redirect(url_for("index"))

@app.post("/checkout")
@login_required
def checkout():
    user=current_user(); c=cart()
    if not c.items:
        flash("Your cart is empty.","error"); return redirect(url_for("index"))
    address=request.form.get("address","").strip()
    discount_type=request.form.get("discount_type","none")
    method=request.form.get("payment_method","").strip()
    if not address:
        flash("Enter your delivery address.","error"); return redirect(url_for("index"))
    try:
        receipt=checkout_facade.checkout(user["name"],c.total,discount_type,method)
        items=[{"name":i["name"],"price":i["price"],"quantity":i["quantity"]} for i in c.items]
        order_id=orders.create_order(user["id"],user["name"],user["email"],address,items,
            receipt["subtotal"],receipt["discount"],receipt["final_total"],receipt)
        session["cart"]=[]
        session["last_order_id"]=order_id
        flash(f"Payment simulation successful. Order #{order_id} placed!","success")
    except ValueError as error:
        flash(str(error),"error")
    return redirect(url_for("index"))

@app.get("/orders/<int:order_id>")
@login_required
def order_detail(order_id):
    order=orders.get_order(order_id); user=current_user()
    if user["role"]!="admin" and order["user_id"]!=user["id"]:
        flash("You cannot view this order.","error"); return redirect(url_for("index"))
    import json
    return render_template("order.html",order=order,items=json.loads(order["items_json"]),user=user)

@app.post("/admin/menu/add")
@admin_required
def add_menu_item():
    try:
        item=MenuItemFactory.create(request.form.get("category",""),request.form.get("name",""),
            request.form.get("description",""),request.form.get("price",""))
        menu_proxy.add_item(item,current_user()); flash("Menu item added.","success")
    except (ValueError,PermissionError) as error: flash(str(error),"error")
    return redirect(url_for("index"))

@app.post("/admin/menu/delete/<int:item_id>")
@admin_required
def delete_menu_item(item_id):
    menu_proxy.delete_item(item_id,current_user()); flash("Menu item deleted.","success")
    return redirect(url_for("index"))

@app.post("/admin/orders/<int:order_id>/advance")
@admin_required
def advance_order(order_id):
    try: orders.advance_order(order_id); flash("Order status advanced.","success")
    except (ValueError,KeyError) as error: flash(str(error),"error")
    return redirect(url_for("index"))

@app.post("/admin/orders/<int:order_id>/cancel")
@admin_required
def cancel_order(order_id):
    try: orders.cancel_order(order_id); flash("Order cancelled.","success")
    except (ValueError,KeyError) as error: flash(str(error),"error")
    return redirect(url_for("index"))

if __name__=="__main__":
    db.initialize()
    app.run(debug=os.getenv("FLASK_DEBUG")=="1",host="0.0.0.0",port=int(os.getenv("PORT",5000)))
