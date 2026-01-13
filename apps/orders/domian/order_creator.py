from decimal import Decimal
from django.db import transaction

from apps.delivery.domian.manager import OrderDeliveryManager
from apps.orders.domian.payment_manager import OrderPaymentManager
from apps.orders.domian.schema import OrderCreateSchema
from apps.orders.models import Order, OrderItem
from apps.products.domain.product_manager import ProductSaleManager
from apps.users.domain.customer_manager import CustomerManager



class OrderCreatorException(Exception):
    pass



class OrderCreator:
    def __init__(self, order_schema: OrderCreateSchema):
        self.order_schema = order_schema

        self._order_instance = None

        self._order_items_instances = list()

        self._order_total_price = Decimal('0.00')
        self._order_total_discount = Decimal('0.00')

        self.customer_manager = CustomerManager(customer_schema=self.order_schema.customer)
        self.product_manager = ProductSaleManager(product_ids = self._get_products_ids())


    def _get_products_ids(self):
        return [i.id for i in self.order_schema.items]

    def _save_order_to_db(self):
        self.order.total_price = self._order_total_price
        self.order.total_discount = self._order_total_discount
        self.order.status = Order.OrderStatus.IN_WORK
        self.order.save()


    def _save_order_items_to_db(self):
        OrderItem.objects.bulk_create(self._order_items_instances)
        self.product_manager.update_queryset_quantity()


    @property
    def order(self):
        if self._order_instance is not None:
            return self._order_instance
        return self.create_order_instance()

    def create_order_instance(self):
        self._order_instance = Order(
            customer =self.customer_manager.customer,
            status=Order.OrderStatus.DRAFT,
            comment=self.order_schema.comment,
        )
        return self._order_instance

    @property
    def order_items(self):
        if self._order_items_instances:
            return self._order_items_instances
        return self._create_order_item_instances()

    def _create_order_item_instances(self):
        for item_schema in self.order_schema.items:
            product = self.product_manager.get_product_by_id(item_schema.product_id)

            order_item = OrderItem(
                    product=product,
                    order = self.order,
                    quantity = item_schema.quantity,
                    price = product.price,
                    discount = product.discount,
                    product_name = product.name,
                )
            self.product_manager.update_product_quantity(
                product_id=product.id,
                sale_qty=item_schema.quantity,
            )

            self._order_items_instances.append(order_item)

            self._update_order_total_prices(order_item)

        return self._order_items_instances



    def _update_order_total_prices(self, order_item: OrderItem):
        quantity = order_item.quantity
        self._order_total_price += (order_item.price * quantity)
        self._order_total_discount += (order_item.discount * quantity)



    def create_order(self):
        with transaction.atomic():
            self._create_order_item_instances()
            self._save_order_to_db()
            self._save_order_items_to_db()
            self.create_delivery()
            self.create_payment()


    def create_delivery(self):
        manager = OrderDeliveryManager(
            order = self.order,
            delivery_schema = self.order_schema.delivery,
        )
        manager.save_delivery()

    def create_payment(self):
        manager = OrderPaymentManager(
            order = self.order,
            payment_schema = self.order_schema.payment,
        )
        manager.create_order_payment()
