from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
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
    def create_user(self, username=None, password=None, **extra_fields):
        email = extra_fields.get("email")
        phone = extra_fields.get("phone")
        if email in ("", None):
            extra_fields.pop("email", None)
        if phone in ("", None):
            extra_fields["phone"] = None

        username = username or extra_fields.get('username') or extra_fields.get('phone') or extra_fields.get('email')
        if not username:
            raise ValueError(_("Username, phone number or email is required"))

        extra_fields.setdefault('username', username)
        user = self.model(**extra_fields)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("staff_status", UserStatuses.DEVELOPER)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(username, password, **extra_fields)


class User(AbstractUser, BaseModel):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("Идетификатор пользователя"),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        validators=[username_validator],
        help_text=_("Используется для входа (email или телефон)"),
        error_messages={"unique": _("Пользователь с таким иднтификатором уже существует.")},
    )

    # персональная информация
    first_name = models.CharField(_("Имя"), max_length=50, blank=True, default='')
    last_name = models.CharField(_("Фамилия"), max_length=50, blank=True, default='')
    # контакты
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email"), unique=True)
    phone = PhoneNumberField(unique=True, verbose_name=_('Номер телефона'), blank=True, null=True)

    telegram_id = models.CharField(max_length=50, blank=True, verbose_name=_("Телеграм ID"), null=True)
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
    USERNAME_FIELD = "username"
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
            return f"{self.username} [{self.staff_status}]"
        return str(self.username)