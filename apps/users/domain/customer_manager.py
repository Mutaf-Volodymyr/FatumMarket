from apps.users.domain.schema import UserSchema
from apps.users.models import User
from base.manager import BaseManager


class CustomerManagerException(Exception):
    pass


class CustomerManager(BaseManager):
    _class_schema = UserSchema
    _class_model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def instance(self):
        if self._instance is None:
            if self._instance_pk is not None:
                self._instance = self._class_model.objects.get(pk=self._instance_pk)
            elif self.schema is not None:
                self._instance = self.get_or_create_customer(self.schema)

        return self._instance

    @classmethod
    def _get_instance_by_schema(cls, schema: _class_schema) -> User | None:
        instance = None
        try:
            if schema.email:
                instance = cls._class_model.objects.get(email=schema.email)
            elif schema.phone:
                instance = cls._class_model.objects.get(phone=schema.phone)
        except cls._class_model.DoesNotExist:
            cls._logger.debug(
                "_get_instance_by_schema: User not found <phone: %s> <email: %s>",
                schema.phone,
                schema.email,
            )
        return instance

    @classmethod
    def create_new_customer(cls, schema: _class_schema, activate: bool = False) -> User | None:
        data = cls._clean_schema_data(schema)
        instance = cls._class_model.objects.create_user(
            **data,
            is_active=activate,
        )
        cls._logger.info("User created: %s", instance)
        if activate:
            cls._logger.info("User activated: %s", instance)

        return instance

    @classmethod
    def activate_customer(cls, instance: User) -> User:
        instance.is_active = True
        instance.save(update_fields=["is_active"])

        cls._logger.info("User activated: %s", instance)

        return instance

    @classmethod
    def bun_customer(cls, instance: User) -> User:
        instance.is_baned = True
        instance.save(update_fields=["is_baned"])

        cls._logger.info("User was baned: %s", instance)

        return instance

    @classmethod
    def get_or_create_customer(
        cls,
        schema: _class_schema,
        activate_if_create: bool = False,
    ) -> User | None:

        instance = cls._get_instance_by_schema(schema)
        if instance is None:
            instance = cls.create_new_customer(schema, activate_if_create)

        return instance

    @classmethod
    def _clean_schema_data(cls, schema: _class_schema) -> dict:
        data = schema.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in list(data.items()):
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    data.pop(key, None)
                else:
                    data[key] = value
        return data
