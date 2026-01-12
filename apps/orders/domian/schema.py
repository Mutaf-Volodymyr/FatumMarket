from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    id: Optional[int]= Field(..., description="ID пользователя (клиента)")
    email: Optional[str]= Field(..., description="Email пользователя (клиента)")
    first_name: Optional[str]= Field(..., description="Имя пользователя (клиента)")
    last_name: Optional[str]= Field(..., description="Фамилия пользователя (клиента)")
    phone: Optional[str]= Field(..., description="Телефон пользователя (клиента)")

class OrderItemSchema(BaseModel):
    """Схема товара в заказе"""
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(..., ge=1, description="Количество")


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



class PaymentSchema(BaseModel):
    """Схема оплаты"""
    payment_status: str = Field(
        default="IN_PROGRESS",
        description="Статус платежа: IN_PROGRESS, paid, cancelled, FAIL, REFUND, PARTIAL_REFUND"
    )
    payment_method: str = Field(
        default="cash",
        description="Метод оплаты: cash, paid"
    )



class OrderCreateSchema(BaseModel):

    customer: UserSchema = Field(..., description='Клиент')
    items: List[OrderItemSchema] = Field(..., min_length=1, description="Товары в заказе")
    delivery: DeliverySchema = Field(..., description="Доставка")
    payment: PaymentSchema = Field(..., description="Оплата")
    comment: Optional[str] = Field(None, max_length=500, description="Комментарий к заказу")
    additional_data: Optional[dict] = Field(None, description="Дополнительные данные (JSON)")

