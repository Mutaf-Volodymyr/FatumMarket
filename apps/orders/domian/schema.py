
from typing import Optional, List
from pydantic import BaseModel, Field

from apps.delivery.domian.schema import DeliverySchema
from apps.users.domain.schema import UserSchema


class OrderItemSchema(BaseModel):
    """Схема товара в заказе"""
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(..., ge=1, description="Количество")




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

