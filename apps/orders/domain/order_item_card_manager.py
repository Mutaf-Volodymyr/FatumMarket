from apps.orders.domain.schema import OrderItemSchema
from apps.products.models import Product
from apps.orders.models import OrderItem
from base.manager import BaseManager


class OrderItemException(Exception):
    pass

class OrderItemCartManager(BaseManager):
    _class_schema = OrderItemSchema
    _class_model = OrderItem


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._product: Product | None = None


    @property
    def product(self):
        if self._product is None:
            if self.schema:
                pk = self.schema.product_id
            elif self.instance:
                pk = self.instance.product_id
            else:
                pk=None
            self._product = Product.objects.get(
                pk=pk,
                is_active=True,
            )

        return self._product


    @property
    def instance(self):
        if self._instance is None:
            if self._instance_pk is not None:
                self._instance = self._class_model.objects.get(pk=self._instance_pk)
            else:
                self._instance = self._class_model.objects.get(
                    product_id = self.schema.product_id,
                    user_id = self.schema.user_id,
                    session_id = self.schema.session_id,
                    status = self._class_model.OrderItemStatus.CARD,

                )
        return self._instance


    def create_cart(self):

        self._validate_quantity(self.schema.quantity)

        self._instance = self._class_model.objects.create(
            **self.schema.model_dump(),
            status = self._class_model.OrderItemStatus.CARD,
        )
        self._logger.info('Created cart item: %s', self._instance)
        return self._instance



    def update_quantity(self, value: int):
        if self.instance is None:
            raise OrderItemException('Экземпляр не существует')

        self._validate_quantity(value)

        if value <= 0:
            return self.delete_cart()

        self.instance.quantity = value
        self.instance.save(update_fields=['quantity'])

        self._logger.debug('Updated cart item qty: %s', self._instance)

        return value



    def delete_cart(self):
        if self.instance is None:
            raise OrderItemException('Экземпляр не существует')
        self.instance.delete()

        self._logger.info('Deleted cart item: %s', self.instance)

        return 0

    def _validate_quantity(self, new_quantity: int):
        if 0 > new_quantity > self.product.quantity:
            raise OrderItemException(
                'Недостаточно товара на складе. Доступно: %s',
                self.product.quantity
            )
