from django.db import models
from django.utils.translation import gettext_lazy as _
from base.for_model import BaseModel, SlugMixin


__all__ = ['Brand']

class Brand(BaseModel, SlugMixin):

    name = models.CharField(max_length=255, verbose_name=_("Название"))
    description = models.TextField(null=True, blank=True, verbose_name=_('Описание'))
    image = models.ImageField(
        upload_to="brands",
        null=True,
        blank=True,
        verbose_name=_('Изображение')
    )

    class Meta:
        verbose_name = _("Бренд")
        verbose_name_plural = _('Бренды')
        db_table = "brands"

    def __str__(self):
        return self.name