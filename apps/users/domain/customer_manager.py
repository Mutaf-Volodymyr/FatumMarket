from apps.users.domain.schema import UserSchema
from apps.users.models import User


class CustomerManagerException(Exception):
    pass


class CustomerManager:
    def __init__(self, customer_schema: UserSchema):
        self.customer_schema = customer_schema
        self._customer_instance = None
        self._is_new_user = False

    @property
    def customer(self):
        if self._customer_instance is not None:
            return self._customer_instance

        if self.customer_schema.id:
            try:
                self._customer_instance = User.objects.get(id=self.customer_schema.id)
            except User.DoesNotExist:
                raise CustomerManagerException(
                    f'User with id={self.customer_schema.id} does not exist'
                )
        else:
            self.create_new_customer()

        return self._customer_instance

    def create_new_customer(self):
        self._customer_instance = User.objects.create_user(
            **self.customer_schema.model_dump(exclude_unset=True)
        )
        self._is_new_user = True
        return self._customer_instance
