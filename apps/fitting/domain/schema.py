from typing import Optional

from pydantic import BaseModel, ValidationError, model_validator

from base.micro_domains import FutureDatetime


class FittingProductSchema(BaseModel):
    product_id: int
    user_id: Optional[int]
    session_id: Optional[str]

    @model_validator(mode="before")
    def check_owner(self):
        if not self.user_id and not self.session_id:
            raise ValueError("Either user_id or session_id must be provided")
        return self


class FittingConfirmSchema(BaseModel):
    class FittingUserSchema(BaseModel):
        user_id: Optional[int]
        phone: str
        first_name: str
        last_name: str

        @model_validator(mode="after")
        def validate_phone(self):
            phone = self.phone.strip()
            if phone.startswith("+"):
                phone_ = phone[1:]
            else:
                phone_ = phone
            if phone_.isdigit():
                return phone
            raise ValidationError("Invalid phone number")

    fitting_id: int
    show_room_id: int
    date: FutureDatetime
    user: FittingUserSchema
