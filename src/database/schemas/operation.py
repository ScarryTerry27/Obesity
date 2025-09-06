from pydantic import BaseModel


class OperationDataInput(BaseModel):
    point: str
    name: str
    value: float | None = None
    unit: str | None = None
    min_value: float | None = None
    max_value: float | None = None


class OperationDataRead(OperationDataInput):
    id: int
    person_id: int

    class Config:
        from_attributes = True
