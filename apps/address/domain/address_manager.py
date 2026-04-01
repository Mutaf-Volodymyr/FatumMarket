from apps.address.domain.schema import AddressSchema, CreateAddressSchema
from apps.address.models import Address
from apps.users.models import User
from base.manager import BaseManager


class AddressManagerException(Exception):
    pass


class AddressManager(BaseManager):
    _class_schema = CreateAddressSchema
    _read_class_schema = AddressSchema
    _class_model = Address

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def get_user_address_schemas(cls, user: User):
        addresses = user.addresses.all()
        result = []

        for address in addresses:
            result.append(cls._read_class_schema(
                id=address.id,
                city=address.city,
                street=address.street,
                house=address.house,
                latitude=address.latitude,
                longitude=address.longitude,
                is_validated=address.is_validated,
            ))

        return result

    @classmethod
    def get_or_create_address(cls, schema: CreateAddressSchema) -> Address:
        data = cls._clean_schema_data(schema)
        instance = cls._class_model.objects.filter(**data).first()

        if instance is None:
            instance = cls.create_new_address(schema)

        return instance

    @classmethod
    def create_new_address(cls, schema: CreateAddressSchema) -> Address:
        data = cls._clean_schema_data(schema)
        instance = cls._class_model.objects.create(**data)
        cls._logger.info('Address created: %s', instance)
        return instance

    @property
    def instance(self):
        if self._instance is None:
            if self._instance_pk is not None:
                self._instance = self._class_model.objects.get(pk=self._instance_pk)
            elif self.schema is not None:
                self._instance = self.get_or_create_address(self.schema)

        return self._instance

    def associate_with_user(self, user: User) -> None:
        if self.instance is not None:
            user.addresses.add(self.instance)
            self._logger.info(
                'User %s associated with Address: %s',
                user, self.instance,
            )
            return
        self._logger.info('Address not found')

    @classmethod
    def _clean_schema_data(cls, schema: CreateAddressSchema) -> dict:
        data = schema.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in list(data.items()):
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    data.pop(key, None)
                else:
                    data[key] = value
        return data
