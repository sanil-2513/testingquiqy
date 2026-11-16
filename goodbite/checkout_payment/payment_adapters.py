from abc import ABC, abstractmethod
from datetime import datetime
from uuid import uuid4

class PaymentProcessor(ABC):
    @abstractmethod
    def pay(self, amount, customer_name): ...
class CardGateway:
    def make_card_payment(self, amount_in_rupees, cardholder_name):
        return {"approved":True,"transaction_code":"CARD-"+uuid4().hex[:8].upper(),
                "charged":round(amount_in_rupees,2),"holder":cardholder_name}
class UpiGateway:
    def transfer_using_upi(self, details):
        return {"status":"SUCCESS","upi_reference":"UPI-"+uuid4().hex[:8].upper(),
                "value":round(details["amount"],2),"account":details["customer"]}
class WalletGateway:
    def withdraw_from_wallet(self, customer, amount_in_paise):
        return {"response_code":200,"wallet_txn":"WALLET-"+uuid4().hex[:8].upper(),
                "debited":int(amount_in_paise),"wallet_user":customer}
def _receipt(method,customer,amount,reference):
    return {"success":True,"method":method,"customer":customer,"amount":round(amount,2),
            "reference":reference,"timestamp":datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "message":"Payment successful (simulation)."}
class CardPaymentAdapter(PaymentProcessor):
    def __init__(self,gateway=None): self.gateway=gateway or CardGateway()
    def pay(self,amount,customer):
        r=self.gateway.make_card_payment(amount,customer)
        return _receipt("Card",r["holder"],r["charged"],r["transaction_code"])
class UpiPaymentAdapter(PaymentProcessor):
    def __init__(self,gateway=None): self.gateway=gateway or UpiGateway()
    def pay(self,amount,customer):
        r=self.gateway.transfer_using_upi({"amount":amount,"customer":customer})
        return _receipt("UPI",r["account"],r["value"],r["upi_reference"])
class WalletPaymentAdapter(PaymentProcessor):
    def __init__(self,gateway=None): self.gateway=gateway or WalletGateway()
    def pay(self,amount,customer):
        r=self.gateway.withdraw_from_wallet(customer,round(amount*100))
        return _receipt("Wallet",r["wallet_user"],r["debited"]/100,r["wallet_txn"])
PAYMENT_METHODS={"card":"Card","upi":"UPI","wallet":"Wallet"}
def get_payment_processor(method):
    choices={"card":CardPaymentAdapter,"upi":UpiPaymentAdapter,"wallet":WalletPaymentAdapter}
    if method not in choices: raise ValueError("Select a valid payment method.")
    return choices[method]()
