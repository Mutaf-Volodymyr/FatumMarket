import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    if not re.fullmatch(r"^\+?\d{1,20}$", value):
        raise ValidationError(
            _(
                "Введите корректный номер телефона "
                "(только цифры, допускается + в начале, максимум 20 символов)."
            )
        )
