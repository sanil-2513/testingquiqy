from .discounts import get_discount_strategy
from .payment_adapters import get_payment_processor, PAYMENT_METHODS

class CheckoutFacade:
    """Facade coordinates discount calculation and simulated payment."""
    def checkout(self,customer_name,amount,discount_type,payment_method):
        customer_name=(customer_name or "").strip()
        if not customer_name: raise ValueError("Customer name is required.")
        try: amount=float(amount)
        except (TypeError,ValueError): raise ValueError("Invalid amount.")
        if amount<=0: raise ValueError("Amount must be greater than zero.")
        if payment_method not in PAYMENT_METHODS: raise ValueError("Select a valid payment method.")
        discount=get_discount_strategy(discount_type).calculate(amount)
        total=round(max(0,amount-discount),2)
        receipt=get_payment_processor(payment_method).pay(total,customer_name)
        receipt.update({"subtotal":round(amount,2),"discount":discount,"final_total":total})
        return receipt
