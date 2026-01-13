from apps.orders.domian.schema import PaymentSchema
from apps.orders.models import Order, OrderPayment


class OrderPaymentException(Exception):
    pass

class OrderPaymentManager:
    def __init__(self, order: Order, payment_schema: PaymentSchema):
        self._order = order
        self._payment_schema = payment_schema
        self._payment = None

    @property
    def payment(self):
        if self._payment is not None:
           self.create_order_payment()
        return self._payment


    def save_payment(self):
        self.payment.save()

    def create_order_payment(self):
        self._payment = OrderPayment(
            order=self._order,
            **self._payment_schema.model_dump(exclude_unset=True),
        )

        return self._payment
