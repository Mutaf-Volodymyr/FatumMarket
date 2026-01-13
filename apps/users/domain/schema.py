from typing import Optional, List
from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    id: Optional[int]= Field(..., description="ID пользователя (клиента)")
    email: Optional[str]= Field(..., description="Email пользователя (клиента)")
    first_name: Optional[str]= Field(..., description="Имя пользователя (клиента)")
    last_name: Optional[str]= Field(..., description="Фамилия пользователя (клиента)")
    phone: Optional[str]= Field(..., description="Телефон пользователя (клиента)")
