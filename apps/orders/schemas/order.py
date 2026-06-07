from typing import Optional

from pydantic import BaseModel, Field


class OrderCreateSchema(BaseModel):
    comment: Optional[str] = Field(None, max_length=500, description="Комментарий к заказу")
