from typing import Optional

from pydantic import BaseModel, model_validator

__all__ = [
    "CreatePickupDeliverySchema",
    "CreateNovaPostaDeliverySchema",
]

from apps.address.schemas import CreateAddressSchema


class CreateDeliverySchema(BaseModel):
    comment: Optional[str]


class CreatePickupDeliverySchema(CreateDeliverySchema):
    pickup_place_id: int


class CreateNovaPostaDeliverySchema(CreateDeliverySchema):
    post_office: Optional[int]
    parcel_locker: Optional[int]
    address: Optional[CreateAddressSchema]

    @model_validator(mode="after")
    def validate_data(self):
        if len(list(filter(bool, [self.post_office, self.parcel_locker, self.address]))) != 1:
            raise ValueError("Не указано место доставки")
