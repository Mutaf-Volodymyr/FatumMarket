from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from base.for_model import BaseModel

__all__ = [
    'User',
    'UserStatuses'
]


class UserStatuses(models.TextChoices):
    OWNER = 'owner', _('Владелец')
    DEVELOPER = "developer", _('Разработчик')
    DELIVERY_MAN = "delivery_man", _("Доставщик")
    SALES_MAN = "sales_man", _("Продавец")
    BOOKER = "booker", _('Бухгалтер')
    MANAGER = 'manager', _("Менеджер")


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError(_("Phone number is required"))

        phone = phone

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("staff_status", UserStatuses.DEVELOPER)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(phone, password, **extra_fields)


class User(AbstractUser, BaseModel):
    username = None

    # персональная информация
    first_name = models.CharField(_("Имя"), max_length=50, blank=True)
    last_name = models.CharField(_("Фамилия"), max_length=50, blank=True)
    # контакты
    email = models.EmailField(_("Email"), blank=True, null=True)
    phone = PhoneNumberField(unique=True, verbose_name=_('Номер телефона'))
    telegram_id = models.CharField(max_length=50, blank=True, verbose_name=_("Телеграм ID"))
    addresses = models.ManyToManyField("address.Address", blank=True, verbose_name=_("Адреса"))
    # статусы
    staff_status = models.CharField(
        max_length=255,
        choices=UserStatuses.choices,
        verbose_name=_("Статус"),
        null=True,
        blank=True
    )
    is_staff = models.BooleanField(_("Статус персонала"), default=False, )
    is_active = models.BooleanField(_("Активный"), default=True, )
    is_baned = models.BooleanField(_("Забанен"), default=False)

    class Meta:
        db_table = "user"
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")



    STATUSES = UserStatuses
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def clean(self):
        if self.is_staff and self.staff_status is None:
            raise ValidationError(_("Определите статус персонала"))
        if self.staff_status and not self.is_staff:
            raise ValidationError(_("Обычный пользователь не может иметь роль персонала"))
        super().clean()

    def __str__(self):
        if self.is_staff:
            return f"{self.first_name} {self.last_name} [{self.staff_status}]"
        return str(self.phone)