from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from apps.users.domain.schema import UserSchema

################## BASE ###################### # noqa: E266


class BaseDeliverySchema(BaseModel):
    """Схема доставки"""

    delivery_type: str = Field(
        default="pickup", description="Способ доставки: pickup, courier, nova_posta"
    )

    address_id: Optional[int] = Field(None, description="ID адреса доставки")
    comment: Optional[str] = Field(None, description="Комментарий к доставке")
    possible_delivery_date: Optional[date] = Field(None, description="Доставка от (желаемая дата)")

    possible_delivery_time_from: Optional[time] = Field(
        None, description="Доставка от (желаемое время)"
    )
    possible_delivery_time_to: Optional[time] = Field(
        None, description="Доставка до (желаемое время)"
    )


################## CREATE ###################### # noqa: E266


class BaseCreateDeliverySchema(BaseDeliverySchema):
    recipient_id: Optional[int] = Field(..., description="ID клиента")


class CreateNovaPostaDeliverySchema(BaseCreateDeliverySchema):
    delivery_type: str = "nova_posta"
    post_office: Optional[int] = Field(None, description="Номер почтового отделения | почтомата")


class CreateCourierDeliverySchema(BaseCreateDeliverySchema):
    delivery_type: str = "courier"
    delivery_cost: Decimal = Field(ge=Decimal("0"), description="Стоимость доставки")

    @model_validator(mode="before")
    def check_possible_delivery_range(cls, values):
        time_from = values.get("possible_delivery_time_from")
        time_to = values.get("possible_delivery_time_to")
        if all([time_from, time_to]):
            if time_from >= time_to:
                raise ValueError("Invalid possible delivery range")
        return values

    @field_validator("possible_delivery_date")
    def possible_delivery_date_past(cls, value):
        if value is not None and value < datetime.now().date():
            raise ValueError("Possible delivery date not be in the past")
        return value


class CreatePickupDeliverySchema(BaseCreateDeliverySchema):
    delivery_type: str = "pickup"
    delivery_cost: Decimal = Field(default=Decimal("0"), description="Стоимость доставки")


################## READ ###################### # noqa: E266


class ReadDeliverySchema(BaseDeliverySchema):
    recipient: UserSchema = Field(..., description="Получатель")

    delivery_type: str = Field(..., description="Способ доставки")
    delivery_cost: Decimal = Field(
        default=Decimal("0"), ge=Decimal("0"), description="Стоимость доставки"
    )
    is_delivered: bool = Field(description="Доставка осуществлена")
    delivered_at: Optional[datetime] = Field(description="Дата доставки")
    returned: Optional[str] = Field(description="Возврат")
