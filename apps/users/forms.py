from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from phonenumbers import NumberParseException, parse

User = get_user_model()


def detect_email_or_phone(value):
    """
    Определяет, является ли значение email или телефоном
    Возвращает ('email', value) или ('phone', parsed_phone) или None
    """
    if not value:
        return None

    value = value.strip()

    # Проверяем, является ли это email
    if "@" in value:
        return ("email", value)

    # Пробуем распарсить как телефон
    try:
        parsed = parse(value, None)
        if parsed:
            # Нормализуем номер телефона
            from phonenumbers import PhoneNumberFormat, format_number

            normalized = format_number(parsed, PhoneNumberFormat.E164)
            return ("phone", normalized)
    except (NumberParseException, Exception):
        pass

    # Если не удалось определить, считаем email (можно ввести)
    return ("email", value)


class LoginForm(forms.Form):
    """Форма входа по email или телефону"""

    login = forms.CharField(
        label="Email или номер телефона",
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "placeholder": "Email или номер телефона",
                "class": "form-control",
            }
        ),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Пароль"}),
    )

    def clean_login(self):
        login = self.cleaned_data.get("login")
        if not login:
            raise ValidationError("Введите email или номер телефона")
        return login


class SignupForm(forms.Form):
    """Форма регистрации с email или телефоном"""

    login = forms.CharField(
        label="Email или номер телефона",
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "placeholder": "Email или номер телефона",
                "class": "form-control",
            }
        ),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Пароль"}),
        min_length=8,
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Повторите пароль"}
        ),
    )

    def clean_login(self):
        login = self.cleaned_data.get("login")
        if not login:
            raise ValidationError("Введите email или номер телефона")

        # Определяем тип (email или phone)
        result = detect_email_or_phone(login)
        if not result:
            raise ValidationError("Введите корректный email или номер телефона")

        login_type, login_value = result

        # Проверяем уникальность
        if login_type == "email":
            if User.objects.filter(email=login_value).exists():
                raise ValidationError("Пользователь с таким email уже существует")
        else:  # phone
            if User.objects.filter(phone=login_value).exists():
                raise ValidationError("Пользователь с таким номером телефона уже существует")

        # Сохраняем тип и значение для использования в save
        self.cleaned_data["login_type"] = login_type
        self.cleaned_data["login_value"] = login_value

        return login

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают")

        return password2

    def clean(self):
        cleaned_data = super().clean()
        login_type = cleaned_data.get("login_type")
        login_value = cleaned_data.get("login_value")

        if not login_type or not login_value:
            raise ValidationError("Введите email или номер телефона")

        return cleaned_data

    def save(self):
        """Создает нового пользователя"""
        login_type = self.cleaned_data["login_type"]
        login_value = self.cleaned_data["login_value"]
        password = self.cleaned_data["password1"]

        # Создаем пользователя
        if login_type == "email":
            user = User.objects.create_user(
                username=login_value,
                email=login_value,
            )
        else:  # phone
            user = User.objects.create_user(
                username=login_value,
                phone=login_value,
            )

        user.set_password(password)
        user.save()
        return user
