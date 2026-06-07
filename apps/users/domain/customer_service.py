from django.db import IntegrityError

from apps.users.domain.schema import UserSchema
from apps.users.models import User
from base.manager import BaseService


class CustomerServiceException(Exception):
    pass


class CustomerService(BaseService):

    def __init__(self, schema: UserSchema):
        self.user_schema = schema
        self._user = None

    def _get_customer_existing(self):
        if self.user_schema.id is not None:
            user = User.objects.filter(id=self.user_schema.id).first()
            if user:
                self._user = user
                return self._user
            raise CustomerServiceException("User pk is not valid")
        if self.user_schema.email:
            user = User.objects.filter(email=self.user_schema.email).first()
            if user:
                self._user = user
                return self._user
        if self.user_schema.phone:
            user = User.objects.filter(phone=self.user_schema.phone).first()
            if user:
                self._user = user
                return self._user

    def create_customer(self):
        if not any((self.user_schema.email, self.user_schema.phone)):
            raise CustomerServiceException("Email or Phone is required for create customer")

        data = self.user_schema.model_dump(exclude_none=True)
        try:
            user = User.objects.create_user(**data)
        except IntegrityError as e:
            raise CustomerServiceException(str(e))
        self._user = user
        return self._user

    @property
    def user(self):
        if self._user is None:
            user = self._get_customer_existing()
            if user:
                self._user = user

            else:
                user = self.create_customer()
                self._user = user

        return self._user
