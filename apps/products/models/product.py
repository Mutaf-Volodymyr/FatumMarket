from decimal import Decimal

from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.for_model import BaseModel, PositionField, PriceField, SlugMixin

__all__ = ["Product", "ProductImage", "ProductSpecification", "ProductGroup", "ProductImageThrough"]


def get_upload_path(instance, filename):
    return f"products/{instance.id}/{filename}"


class Product(BaseModel, SlugMixin):
    class Meta:
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")
        db_table = "product"
        indexes = [
            models.Index(
                fields=["name"],
            ),
        ]

    name = models.CharField(max_length=256, verbose_name=_("Название"))

    description = models.TextField(null=True, blank=True, verbose_name=_("Описание"))
    is_active = models.BooleanField(default=False, verbose_name=_("Активно"))
    # количество
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Количество"),
        help_text="Доступное для продажи",
    )
    # цены
    price = PriceField(verbose_name=_("Цена"))
    old_price = PriceField(verbose_name=_("Старая цена"), null=True, blank=True)
    # связи
    category = models.ForeignKey(
        to="products.Category",
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Категория"),
    )
    brand = models.ForeignKey(
        to="Brand",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Бренд"),
    )
    specifications = models.ManyToManyField(
        to="products.SpecificationValue",
        related_name="products",
        through="products.ProductSpecification",
    )
    group = models.ForeignKey(
        to="products.ProductGroup",
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
        verbose_name=_("Группа товаров"),
    )

    @property
    @admin.display(description=_("Скидка"))
    def discount(self):
        if not self.price:
            return Decimal("0.00")
        if not self.old_price:
            return Decimal("0.00")
        discount = (self.old_price - self.price) / self.old_price
        return Decimal(discount * 100).quantize(Decimal("0.01"))

    @property
    def has_discount(self):
        return self.discount > 0

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.group_id:
            group, created = ProductGroup.objects.get_or_create(
                name=self.name,
                defaults={
                    "description": self.description,
                    "category": self.category,
                },
            )
            self.group = group

        return super().save(*args, **kwargs)


class ProductImageThrough(BaseModel):
    product = models.ForeignKey(
        to="products.Product",
        on_delete=models.CASCADE,
        related_name="images_through",
    )
    image = models.ForeignKey(
        to="products.ProductImage",
        on_delete=models.CASCADE,
        related_name="images_through",
    )
    position = PositionField()

    class Meta:
        verbose_name = _("Изображение товара [позиция]")
        verbose_name_plural = _("Изображение товаров [позиция]")
        db_table = "product_image_through"
        ordering = ("position",)

    def __str__(self):
        return _("Изображение товара: ") + str(self.product.name)

    def __repr__(self):
        return f"ProductImage('{self.image}' -> {self.product.name})"


class ProductImage(BaseModel):
    image = models.ImageField(upload_to=get_upload_path, verbose_name=_("Изображение"))
    products = models.ManyToManyField(
        to="products.Product",
        through="products.ProductImageThrough",
        related_name="images",
    )

    class Meta:
        verbose_name = _("Изображение товара")
        verbose_name_plural = _("Изображение товаров")
        db_table = "product_image"

    def __str__(self):
        return _("Изображение товара: ") + str(self.id)

    def __repr__(self):
        return f"ProductImage('{self.id}' -> {self.image.path})"


class ProductSpecification(BaseModel):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        verbose_name=_("Товар"),
        related_name="product_specification",
    )

    specification_value = models.ForeignKey(
        "products.SpecificationValue",
        on_delete=models.CASCADE,
        related_name="product_specification",
        verbose_name=_("Значение спецификаций"),
    )

    specification_name = models.ForeignKey(
        "products.SpecificationName",
        on_delete=models.CASCADE,
        related_name="products_specification",
        verbose_name=_("Название спецификации"),
        editable=False,
    )

    def save(self, *args, **kwargs):
        if self.specification_name_id is None:
            self.specification_name_id = self.specification_value.specification_name_id
        return super().save(*args, **kwargs)

    class Meta:
        db_table = "product_specification"
        verbose_name = _("Спецификация товара")
        verbose_name_plural = _("Спецификации товара")
        constraints = [
            models.UniqueConstraint(
                fields=["product", "specification_name"], name="unique_product_specification_name"
            )
        ]

    def __str__(self):
        return f"{self.product} | {self.specification_value}"


class ProductGroup(BaseModel):
    name = models.CharField(max_length=256, unique=True, verbose_name=_("Название"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Описание"))
    category = models.ForeignKey(
        to="products.Category",
        on_delete=models.PROTECT,
        related_name="product_groups",
        verbose_name=_("Категория"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Группа товаров")
        verbose_name_plural = _("Группы товаров")
