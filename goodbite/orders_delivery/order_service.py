import json
from datetime import datetime
from sqlalchemy import text
from .order import Order
from .order_states import STATE_CLASSES

class OrderService:
    def __init__(self,database,notification_center):
        self.db,self.notification_center=database,notification_center
    def create_order(self,user_id,customer,email,address,items,subtotal,discount,total,payment):
        with self.db.engine.begin() as con:
            result=con.execute(text("""INSERT INTO orders
                (user_id,customer,email,address,items_json,subtotal,discount,total,payment_method,
                 payment_reference,status,created_at)
                VALUES (:uid,:customer,:email,:address,:items,:subtotal,:discount,:total,:method,:ref,
                        'Placed',:created) RETURNING id"""),
                {"uid":user_id,"customer":customer,"email":email,"address":address,
                 "items":json.dumps(items),"subtotal":subtotal,"discount":discount,"total":total,
                 "method":payment["method"],"ref":payment["reference"],
                 "created":datetime.now().strftime("%d-%m-%Y %H:%M")})
            order_id=result.scalar_one()
        order=Order(order_id,customer,", ".join(x["name"] for x in items),address)
        self.notification_center.notify(order,"Your order has been placed.")
        return order_id
    def get_order(self,order_id):
        with self.db.engine.connect() as con:
            row=con.execute(text("SELECT * FROM orders WHERE id=:id"),{"id":order_id}).mappings().first()
        if not row: raise KeyError("Order not found.")
        return dict(row)
    def get_all_orders(self,user=None):
        sql="SELECT * FROM orders ORDER BY id DESC"
        params={}
        if user and user["role"]!="admin":
            sql="SELECT * FROM orders WHERE user_id=:uid ORDER BY id DESC"; params={"uid":user["id"]}
        with self.db.engine.connect() as con:
            return [dict(r) for r in con.execute(text(sql),params).mappings()]
    def _change(self,order_id,action):
        row=self.get_order(order_id)
        state_cls=STATE_CLASSES.get(row["status"])
        if not state_cls: raise ValueError("Unknown order status.")
        order=Order(row["id"],row["customer"],", ".join(x["name"] for x in json.loads(row["items_json"])),row["address"],state_cls(),row["created_at"])
        previous=order.status
        if action=="advance": order.advance()
        else: order.cancel()
        with self.db.engine.begin() as con:
            con.execute(text("UPDATE orders SET status=:s WHERE id=:id"),{"s":order.status,"id":order.id})
        self.notification_center.notify(order,f"Order status changed from {previous} to {order.status}.")
        return order
    def advance_order(self,order_id): return self._change(order_id,"advance")
    def cancel_order(self,order_id): return self._change(order_id,"cancel")
