from pydantic import BaseModel, Field


class OrderItemSchema(BaseModel):
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(default=1, ge=1, description="Количество")
