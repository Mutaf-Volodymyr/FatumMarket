from decimal import Decimal
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('Создано'))
    updated_at = models.DateTimeField(auto_now=True, editable=False, verbose_name=_('Обновлено'))

    history = HistoricalRecords(user_model='users.User')

    def __str__(self):
        name = getattr(self, 'name', None)
        if name:
            return name
        return super().__str__()

    class Meta:
        abstract = True

    @classmethod
    def get_fields_list(cls):
        return [field.name for field in cls._meta.fields]


class PriceField(models.DecimalField):
    def __init__(
        self,
        verbose_name=None,
        **kwargs,
    ):
        kwargs.setdefault('max_digits', 12)
        kwargs.setdefault('decimal_places', 2)
        kwargs.setdefault('null', True)
        kwargs.setdefault('blank', True)
        kwargs.setdefault('validators', [MinValueValidator(Decimal('0.01'))])
        super().__init__(verbose_name, **kwargs)


class PositionField(models.PositiveIntegerField):
    def __init__(
        self,
        **kwargs,
    ):
        kwargs.setdefault('verbose_name', _('Позиция'))
        kwargs.setdefault('default', 0)
        super().__init__(**kwargs)

