from abc import ABC, abstractmethod
from typing import Optional

from django.db.models import Model as DjangoModel
from pydantic import BaseModel as PydanticSchema

from logging import getLogger


class BaseManager(ABC):
    _class_schema: PydanticSchema
    _class_model: DjangoModel

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._logger = getLogger(cls.__name__)

    def __init__(
            self,
            *,
            instance_pk: Optional[int] = None,
            instance: Optional[DjangoModel] = None,
            data: Optional[dict] = None,
    ):
        self._data = data
        self._instance_pk = instance_pk
        self._instance = instance
        self._schema = None

    @property
    def schema(self) -> PydanticSchema:
        if self._schema is None:
            if self._data is not None:
                self._schema = self._class_schema.model_validate(self._data)
        return self._schema

    @property
    @abstractmethod
    def instance(self) -> DjangoModel | None:
        pass
