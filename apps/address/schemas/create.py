from typing import Optional

from pydantic import BaseModel


class CreateAddressSchema(BaseModel):
    raw_address: Optional[str]
