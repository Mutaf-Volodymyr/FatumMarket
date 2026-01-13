from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from phonenumbers import parse, NumberParseException
from phonenumbers import format_number, PhoneNumberFormat

User = get_user_model()


class PhoneOrEmailBackend(ModelBackend):
    """
    Custom authentication backend that allows login with either phone or email
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('phone') or kwargs.get('email')
        
        if username is None or password is None:
            return None
        
        user = None
        
        # Определяем, является ли это email или телефон
        if '@' in username:
            # Это email
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
        else:
            # Пробуем как телефон
            try:
                parsed = parse(username, None)
                if parsed:
                    normalized = format_number(parsed, PhoneNumberFormat.E164)
                    try:
                        user = User.objects.get(phone=normalized)
                    except User.DoesNotExist:
                        # Попробуем найти по частичному совпадению
                        try:
                            user = User.objects.get(phone__icontains=username.replace('+', '').replace('-', '').replace(' ', ''))
                        except (User.DoesNotExist, User.MultipleObjectsReturned):
                            return None
            except (NumberParseException, Exception):
                return None
        
        if user and user.check_password(password):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
