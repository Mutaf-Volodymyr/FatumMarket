from datetime import datetime


class FutureDatetime(datetime):
    def __new__(cls, value, *args, **kwargs):
        if isinstance(value, str):
            instance = datetime.fromisoformat(value)
            instance = datetime.__new__(
                cls,
                instance.year,
                instance.month,
                instance.day,
                instance.hour,
                instance.minute,
                instance.second,
            )
        else:
            instance = super().__new__(cls, value, *args, **kwargs)
        cls.validate_future(instance)
        return instance

    @classmethod
    def validate_future(cls, instance):
        if datetime.now() > instance:
            raise ValueError("Дата должна быть в будущем")
