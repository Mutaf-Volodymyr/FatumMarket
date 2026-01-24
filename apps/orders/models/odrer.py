from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from base.for_model import BaseModel, PriceField
from config import settings
from django.contrib.sessions.models import Session

__all__ = ['Order', 'OrderItem', 'OrderPayment']



class Order(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_('Клиент'),
        null=True,
        blank=True
    )
    session = models.ForeignKey(
        Session,
        on_delete=models.SET_NULL,
        verbose_name=_('Сессия'),
        null=True,
        blank=True
    )

    class OrderStatus(models.TextChoices):
        DRAFT = 'draft', _("Черновик")
        IN_WORK = 'in_work', _("В работе")
        COMPLETED = 'completed', _("Выполнен")

    status = models.CharField(
        max_length=100,
        default=OrderStatus.DRAFT,
        choices=OrderStatus.choices,
        verbose_name=_("Статус")
    )
    total_price = PriceField(verbose_name=_('Общая цена'))
    total_discount = PriceField(verbose_name=_('Общая скидка'), default=0)
    comment = models.TextField(
        max_length=500,
        verbose_name=_("Комментарий к заказу"),
        null=True,
        blank=True,
    )
    additional_data = JSONField(
        blank=True,
        null=True,
        verbose_name=_("Additional Data"),
    )


    @property
    def price_with_discount(self):
        return self.total_price + self.total_discount



    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _('Заказы')
        db_table = "orders"

    def __str__(self):
        return f"{self.pk} | {self.status}"



class OrderItem(BaseModel):
    order = models.ForeignKey(
        'Order',
        on_delete=models.PROTECT,
        related_name='items',
        verbose_name=_("Заказ"),
        null=True,
        blank=True,

    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True, blank=True,
    )
    session = models.ForeignKey(
        Session,
        on_delete=models.SET_NULL,
        verbose_name=_('Сессия'),
        null=True,
        blank=True
    )

    class OrderItemStatus(models.TextChoices):
        CARD = 'card', _("Корзина")
        ORDER = 'order', _("Заказ")

    status = models.CharField(
        max_length=100,
        choices=OrderItemStatus.choices,
        default=OrderItemStatus.CARD,
    )

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name=_("Товар")
    )
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Количество"),
    )
    price = PriceField(verbose_name=_('Цена продажи'), null=True, blank=True)
    discount = PriceField(verbose_name=_('Скидка'), default=0)
    product_name = models.CharField(max_length=256, verbose_name='Название товара', null=True, blank=True)


    def __str__(self):
        return f"{self.order_id} | {self.product_name} | {self.quantity}"


    class Meta:
        verbose_name = _("Состав заказа")
        verbose_name_plural = _('Состав заказа')
        db_table = "order_items"




class OrderPayment(BaseModel):
    order = models.OneToOneField(
        'Order',
        on_delete=models.PROTECT,
        related_name='payment',
    )

    class PaymentStatusChoices(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', _('В процессе')
        PAID = 'paid', _('Оплачен')
        CANCELLED = 'cancelled', _('Отменен')
        FAIL = 'FAIL', _('Провален')
        REFUND = 'REFUND', _('Отменен')
        PARTIAL_REFUND = 'PARTIAL_REFUND', _('Частично отменен')

    payment_status = models.CharField(
        max_length=100,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.IN_PROGRESS,
        verbose_name=_('Статус платежа'),
    )

    class PaymentMethodChoices(models.TextChoices):
        CASH = 'cash', _('Наличная')
        CARD = 'paid', _('Безналичная')

    payment_method = models.CharField(
        max_length=100,
        choices=PaymentMethodChoices.choices,
        default=PaymentMethodChoices.CASH,
        verbose_name=_('Метод оплаты')
    )


    class Meta:
        verbose_name = _("Оплата заказа")
        verbose_name_plural = _('Оплата заказов')
        db_table = "order_payment"


    def __str__(self):
        return f"{self.order} | ({self.payment_method}) | {self.payment_status}"
