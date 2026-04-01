from typing import Optional, List
from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    id: Optional[int] = Field(None, description="ID пользователя (клиента)")
    email: Optional[str] = Field(None, description="Email пользователя (клиента)")
    first_name: Optional[str] = Field(None, description="Имя пользователя (клиента)")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя (клиента)")
    phone: Optional[str] = Field(None, description="Телефон пользователя (клиента)")
