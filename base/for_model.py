from decimal import Decimal
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
import ulid

try:
    from unidecode import unidecode
except ImportError:
    # Fallback транслитерация для кириллицы
    def unidecode(text):
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
        }
        return ''.join(translit_map.get(char, char) for char in text)




class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_('Создано'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name=_('Обновлено'),
    )

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



class SlugMixin(models.Model):
    """Миксин для автоматической генерации slug из поля name"""
    slug = models.SlugField(
        max_length=255,
        unique=True,
        editable=False,
        verbose_name=_('Slug'),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            # Получаем значение name
            name = getattr(self, 'name', '')
            if name:
                # Транслитерация кириллицы в латиницу
                transliterated = unidecode(str(name))
                # Создаем slug
                base_slug = slugify(transliterated)
                unique_slug = base_slug
                num = 1

                # Проверяем уникальность slug
                model_class = self.__class__
                while model_class.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                    unique_slug = f"{base_slug}-{num}"
                    num += 1

                self.slug = unique_slug
        super().save(*args, **kwargs)


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


def generate_ulid():
    return ulid.new().str


class UlidPrimaryKeyMixin(models.Model):
    id = models.CharField(
        max_length=26,
        default=generate_ulid,
        primary_key=True,
        null=False,
        editable=False,
    )

    class Meta:
        abstract = True
