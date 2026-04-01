from decimal import Decimal

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Sum
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from base.for_model import BaseModel, PriceField

__all__ = [
    "Supply",
    "Supplier",
    "ProductSupply",
]


class Supplier(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Название"))
    email = models.EmailField(null=True, blank=True, unique=True)
    phone = PhoneNumberField(verbose_name=_("Номер телефона"), unique=True, null=True, blank=True)

    class Meta:
        verbose_name = _("Поставщик")
        verbose_name_plural = _("Поставщики")
        db_table = "supplier"


class Supply(BaseModel):
    supplier = models.ForeignKey(
        to="supply.Supplier",
        on_delete=models.CASCADE,
        related_name="supply",
        verbose_name=_("Поставщик"),
    )
    products = models.ManyToManyField(
        to="products.Product", verbose_name=_("Товары"), through="supply.ProductSupply"
    )
    # coast
    is_batch_paid = models.BooleanField(default=False, verbose_name=_("Товар оплачен"))

    import_coast = PriceField(verbose_name=_("Стоимость растаможки"))
    is_import_paid = models.BooleanField(default=False, verbose_name=_("Растаможка оплачена"))

    # dates
    sent_at = models.DateField(verbose_name=_("Дата отправки"), null=True, blank=True)
    received_at = models.DateField(verbose_name=_("Дата получения"), null=True, blank=True)

    def clean(self):
        if self.received_at and self.sent_at and self.sent_at >= self.received_at:
            raise ValidationError(
                _('"Дата отправки" не может быть раньше и равной "Дате получения"')
            )

    @property
    @admin.display(description=_("Стоимость партии"))
    def batch_cost(self) -> Decimal:
        total = self.products_through.aggregate(total=Sum(F("purchase_price") * F("qty")))["total"]
        return total or Decimal("0")

    @property
    @admin.display(description=_("Наценка"))
    def batch_revenue(self) -> Decimal:
        total = self.products_through.aggregate(total=Sum(F("product__price") * F("qty")))["total"]
        return total or Decimal("0")

    @property
    @admin.display(description=_("Наценка в %"))
    def markup_percent(self) -> Decimal:
        cost = self.batch_cost
        if cost == 0:
            return Decimal("0")
        revenue = self.batch_revenue
        return ((revenue - cost) / cost * 100).quantize(Decimal("0.01"))

    def __str__(self):
        date_format = "%d-%m-%y"
        unknown = "??-??-??"
        sent_at = self.sent_at.strftime(date_format) if self.sent_at else unknown
        received_at = self.received_at.strftime(date_format) if self.received_at else unknown
        return f"{self.supplier.name} | {sent_at} - {received_at}"

    class Meta:
        verbose_name = _("Партия товара")
        verbose_name_plural = _("Партии товаров")
        db_table = "supply"
        ordering = ("-sent_at",)


class ProductSupply(BaseModel):
    supply = models.ForeignKey(
        to="supply.Supply",
        on_delete=models.PROTECT,
        related_name="products_through",
        verbose_name=_("Поставщик"),
    )
    product = models.ForeignKey(
        to="products.Product",
        on_delete=models.PROTECT,
        related_name="supply_through",
        verbose_name=_("Товар"),
    )
    purchase_price = PriceField(
        verbose_name=_("Закупочная цена [MLD]"),
        help_text=_("Заполнять не нужно. Пересчитается автоматически по курсу"),
    )
    purchase_price_usd = PriceField(verbose_name=_("Закупочная цена [USD]"))
    qty = models.PositiveIntegerField(verbose_name=_("Количество"))

    def __str__(self):
        return f"{self.product.name} | {self.qty}"

    class Meta:
        verbose_name = _("Товар в партии")
        verbose_name_plural = _("Товары в партии")
        db_table = "product_supply_m2m"
