from apps.address.models import Address
from apps.address.schemas import AddressSchema, CreateAddressSchema
from apps.users.models import User
from base.manager import BaseService


class AddressServiceException(Exception):
    pass


class AddressService(BaseService):
    _read_class_schema = AddressSchema
    _class_model = Address

    @classmethod
    def get_user_address_schemas(cls, user: User):
        addresses = user.addresses.all()
        result = []

        for address in addresses:
            result.append(
                cls._read_class_schema(
                    id=address.id,
                    city=address.city,
                    street=address.street,
                    house=address.house,
                    latitude=address.latitude,
                    longitude=address.longitude,
                    is_validated=address.is_validated,
                )
            )

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
        cls._logger.info("Address created: %s", instance)
        return instance

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
