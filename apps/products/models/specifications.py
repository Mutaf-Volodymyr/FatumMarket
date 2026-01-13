from django.core.exceptions import ValidationError
from django.db import models

from base.for_model import BaseModel, AuditMixin
from django.utils.translation import gettext_lazy as _


__all__ = ['SpecificationName', 'SpecificationValue',]

class SpecificationName(AuditMixin):
    name = models.CharField(max_length=255, verbose_name=_("Название"))
    position = models.IntegerField(default=100, verbose_name=_("Position"))
    unit_measurement = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Единица измерения"),
    )

    class Meta:
        db_table = 'specification_name'
        verbose_name = _("Название спецификации")
        verbose_name_plural = _('Название спецификаций')

    def __str__(self):
        return self.name






class SpecificationValue(AuditMixin):
    specification_name = models.ForeignKey(
        SpecificationName,
        on_delete=models.CASCADE,
        related_name="values",
        verbose_name=_("Название спецификации"),

    )
    value = models.CharField(max_length=255, verbose_name=_("Название"))

    class Meta:
        db_table = 'specification_value'
        verbose_name = _("Значение спецификации")
        verbose_name_plural = _('Значение спецификаций')


    def __str__(self):
        return f"{self.specification_name.name} : {self.value}"
