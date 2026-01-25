from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from phonenumbers import parse, NumberParseException
from phonenumbers import format_number, PhoneNumberFormat

User = get_user_model()


class PhoneOrEmailBackend(ModelBackend):
    """
    Custom authentication backend that allows login with either phone or email
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        login_value = username.strip()
        query = Q(username=login_value) | Q(email=login_value)

        if '@' not in login_value:
            try:
                parsed = parse(login_value, None)
                normalized = format_number(parsed, PhoneNumberFormat.E164)
                query = query | Q(phone=normalized) | Q(username=normalized)
                login_value = normalized
            except NumberParseException:
                query = query | Q(phone=login_value)

        try:
            user = User.objects.get(query)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
