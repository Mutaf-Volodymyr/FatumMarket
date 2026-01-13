
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from apps.users.domain.schema import UserSchema


class DeliverySchema(BaseModel):
    """Схема доставки"""
    delivery_type: str = Field(
        default="pickup",
        description="Способ доставки: pickup, courier, nova_posta"
    )
    recipient: UserSchema = Field(..., description='Получатель')
    address_id: Optional[int] = Field(None, description="ID адреса доставки")
    comment: Optional[str] = Field(None, description="Комментарий к доставке")
    urgency: str = Field(
        default="standard",
        description="Срочность: quickly, standard"
    )
    possible_delivery_time_from: Optional[datetime] = Field(
        None,
        description="Доставка от (желаемое время)"
    )
    possible_delivery_time_to: Optional[datetime] = Field(
        None,
        description="Доставка до (желаемое время)"
    )
    delivery_cost: Decimal = Field(
        default=Decimal("0"),
        ge=Decimal("0"),
        description="Стоимость доставки"
    )
