
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class OrderItemSchema(BaseModel):
    user_id: Optional[int] = Field(None, ge=0)
    session_id: Optional[str] = None
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(default=1, ge=1, description="Количество")

    @model_validator(mode="after")
    def check_owner(self):
        if not self.user_id and not self.session_id:
            raise ValueError("Either user_id or session_id must be provided")
        return self
