from apps.orders.models import Order, OrderPayment
from apps.orders.schemas import PaymentSchema


class OrderPaymentException(Exception):
    pass


class OrderPaymentService:
    def __init__(
        self,
        order: Order,
    ):
        self._order = order
        self._payment = None

    @property
    def payment(self):
        if self._payment is None:
            self._payment = self._order.payment
        return self._payment

    def create(self, payment_schema: PaymentSchema):
        self._payment = OrderPayment.objects.create(
            order=self._order,
            **payment_schema.model_dump(exclude_unset=True),
        )
        return self._payment
