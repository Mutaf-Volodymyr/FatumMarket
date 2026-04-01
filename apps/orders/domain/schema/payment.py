from pydantic import BaseModel, Field


class PaymentSchema(BaseModel):
    """Схема оплаты"""

    payment_status: str = Field(
        default="IN_PROGRESS",
        description="Статус платежа: IN_PROGRESS, paid, cancelled, FAIL, REFUND, PARTIAL_REFUND",
    )
    payment_method: str = Field(default="cash", description="Метод оплаты: cash, paid")
