from pydantic import BaseModel
from database.parameters import PARAMETER_KEYS


class OperationPointInput(BaseModel):
    point: str
    data: dict[str, str | None]


class OperationPointRead(BaseModel):
    id: int
    person_id: int
    point: str
    data: dict[str, str | None]

    @classmethod
    def from_orm(cls, obj) -> "OperationPointRead":
        data = {k: getattr(obj, k) for k in PARAMETER_KEYS}
        return cls(id=obj.id, person_id=obj.person_id, point=obj.point, data=data)
