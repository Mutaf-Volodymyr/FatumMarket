from decimal import Decimal
from typing import Optional

from django.db import transaction

from apps.delivery.models import Delivery
from apps.orders.domian.schema import OrderCreateSchema, OrderItemSchema, PaymentSchema, DeliverySchema
from apps.orders.models import Order, OrderItem, OrderPayment
from apps.products.models import Product
from apps.users.models import User

class OrderCreatorException(Exception):
    pass

class OrderPaymentException(Exception):
    pass

class OrderDeliveryException(Exception):
    pass


class OrderCreator:
    def __init__(self, order_schema: OrderCreateSchema):
        self.order_schema = order_schema

        self._order_instance = None
        self._customer_instance = None
        self._order_items_instances = list()
        self._order_payment_instance = None
        self._order_delivery_instance = None

        self._is_new_user = False

        self._products_dict = None

        self._order_total_price = Decimal('0.00')
        self._order_total_discount = Decimal('0.00')


    @property
    def customer(self):
        if self._customer_instance is not None:
            return self._customer_instance

        if self.order_schema.customer.id:
            try:
                self._customer_instance = User.objects.get(id=self.order_schema.customer.id)
            except User.DoesNotExist:
                raise OrderCreatorException(
                    f'User with id={self.order_schema.id} does not exist'
                )
        else: self.create_new_user()

        return self._customer_instance

    @property
    def products_dict(self):
        if self._products_dict is not None:
            return self._products_dict

        items_schema = self.order_schema.items

        if not items_schema:
            raise OrderCreatorException('No products')

        product_ids = set(map(lambda x: x.product_id, items_schema))

        self._products_dict = {
            i.id : i for i in Product.objects.select_for_update().filter(
                pk__in=product_ids,
                is_active=True,
            ).distinct()
        }
        if len(self._products_dict) != len(product_ids):
            raise OrderCreatorException(
                'Not all products found'
            )

        return self._products_dict

    def _update_products(self):
        Product.objects.bulk_update(self.products_dict.values(), fields=['quantity'])

    def _save_order_to_db(self):
        self.order.total_price = self._order_total_price
        self.order.total_discount = self._order_total_discount
        self.order.status = Order.OrderStatus.IN_WORK
        self.order.save()


    def _save_order_items_to_db(self):
        OrderItem.objects.bulk_create(self._order_items_instances)
        self._update_products()


    def create_new_user(self):
        self._customer_instance = User.objects.create_user(
            **self.order_schema.customer.model_dump(exclude_unset=True)
        )
        self._is_new_user = True
        return self._customer_instance



    @property
    def order(self):
        if self._order_instance is not None:
            return self._order_instance
        return self.create_order_instance()

    def create_order_instance(self):
        self._order_instance = Order(
            customer =self.customer,
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
            product: Product = self.products_dict[item_schema.product_id]
            if product.quantity < item_schema.quantity:
                raise OrderCreatorException(
                    'Not enough quantity for product {}'.format(item_schema.product_id)
                )
            order_item = OrderItem(
                    product=product,
                    order = self.order,
                    quantity = item_schema.quantity,
                    price = product.price,
                    discount = item_schema.discount,
                    product_name = product.name,
                )

            self._order_items_instances.append(order_item)

            self._update_order_prices(order_item)

            self._update_product_quantity(
                order_item=order_item,
                product=product,
            )
        return self._order_items_instances



    def _update_order_prices(self, order_item: OrderItem):
        quantity = order_item.quantity
        self._order_total_price += (order_item.price * quantity)
        self._order_total_discount += (order_item.discount * quantity)


    def _update_product_quantity(self, *, order_item: OrderItem, product: Product):
        product.quantity -= order_item.quantity


    @property
    def order_payment(self):
        if self._order_payment_instance is not None:
            return self._order_payment_instance
        return self.create_order_payment_instance()

    def create_order_payment_instance(self):
        manager = OrderPaymentManager(
            order = self.order,
            payment_schema=self.order_schema.payment,
        )
        self._order_payment_instance = manager.make_payment()

        return self._order_payment_instance


    @property
    def order_delivery(self):
        if self._order_delivery_instance is not None:
            return self._order_delivery_instance
        return self.create_order_delivery_instance()

    def create_order_delivery_instance(self):
        manager = OrderDeliveryManager(
            order = self.order,
            delivery_schema=self.order_schema.delivery,
        )
        self._order_delivery_instance = manager.make_delivery()

        return self._order_delivery_instance



    def create_order(self):
        with transaction.atomic():
            self._create_order_item_instances()
            self._save_order_to_db()
            self._save_order_items_to_db()
            self.order_payment.save()
            self.order_delivery.save()




class OrderPaymentManager:
    def __init__(self, order: Order, payment_schema: Optional[PaymentSchema] = None):
        self._order = order
        self._payment = payment_schema

    def make_payment(self):
        if self._payment is not None:
            return OrderPayment(
                    order=self._order,
                    ** self._payment.model_dump(exclude_unset=True),
                )
        raise OrderPaymentException(
            'Not Schema to make payment'
        )



class OrderDeliveryManager:
    def __init__(self, order: Order, delivery_schema: Optional[DeliverySchema] = None):
        self._order = order
        self._delivery = delivery_schema


    def make_delivery(self):
        if self._delivery is not None:
            return Delivery(
                order=self._order,
                **self._delivery.model_dump(exclude_unset=True)
            )