from datetime import datetime


class FutureDatetime(datetime):
    def __new__(cls, *args, **kwargs):
        instance = super(FutureDatetime, cls).__new__(cls, *args, **kwargs)
        instance = cls.validate_future(instance)
        return instance

    @classmethod
    def validate_future(cls, instance):
        current_datetime = datetime.now()
        if current_datetime > instance:
            raise ValueError("Future date cannot be greater than current date")
        return instance
