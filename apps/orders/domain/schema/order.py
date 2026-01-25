from typing import Optional, List
from pydantic import BaseModel, Field

from apps.users.domain.schema import UserSchema

class OrderCreateSchema(BaseModel):

    # customer: UserSchema = Field(..., description='Клиент')
    # items: List[int] = Field(..., min_length=1, description="Товары в заказе")
    # delivery: DeliverySchema = Field(..., description="Доставка")
    # payment: PaymentSchema = Field(..., description="Оплата")
    comment: Optional[str] = Field(None, max_length=500, description="Комментарий к заказу")
    additional_data: Optional[dict] = Field(None, description="Дополнительные данные (JSON)")

