from pydantic import BaseModel


class OperationDataInput(BaseModel):
    point: str
    name: str
    value: str | None = None
    unit: str | None = None
    min_value: str | None = None
    max_value: str | None = None


class OperationDataRead(OperationDataInput):
    id: int
    person_id: int

    class Config:
        from_attributes = True
