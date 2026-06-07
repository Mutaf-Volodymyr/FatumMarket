from abc import ABC
from logging import getLogger


class BaseService(ABC):
    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        cls._logger = getLogger(cls.__name__)

    def _validate_user(self, user):
        if user is None:
            return None
        if user.is_anonymous:
            return None
        return user
