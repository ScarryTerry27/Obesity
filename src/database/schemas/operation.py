from pydantic import BaseModel


class OperationPointInput(BaseModel):
    point: str
    data: dict[str, str | None]


class OperationPointRead(OperationPointInput):
    id: int
    person_id: int

    class Config:
        from_attributes = True
