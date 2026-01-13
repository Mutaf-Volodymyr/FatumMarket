from django.contrib import admin
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from apps.products.models.product import Product
from base.for_model import PositionField, AuditMixin, SlugMixin
from django.utils.translation import gettext_lazy as _


__all__ = [
    "Category",
]

class Category(MPTTModel, AuditMixin, SlugMixin):

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('Название'),
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    position = PositionField()
    image = models.ImageField(
        upload_to='categories',
        null=True,
        blank=True,
        verbose_name=_('Изображение')
    )

    

    @property
    def products(self):
        return Product.objects.filter(
            category__in=self.get_descendants(include_self=True)
        )

    @property
    @admin.display(description=_('Количество продуктов'))
    def products_count(self):
        return self.products.count()

    class MPTTMeta:
        order_insertion_by = ['position']

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")
        indexes = [
            models.Index(
                fields=["name"],
            ),
        ]
        db_table = "category"

    def __str__(self):
        return self.name





