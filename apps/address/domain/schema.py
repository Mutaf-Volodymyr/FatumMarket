from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class AddressSchema(BaseModel):
    id: Optional[int]
    city: Optional[str]
    street: Optional[str]
    house: Optional[str]

    latitude: Optional[Decimal]
    longitude: Optional[Decimal]

    is_validated: Optional[bool]


class CreateAddressSchema(BaseModel):
    raw_address: Optional[str]
