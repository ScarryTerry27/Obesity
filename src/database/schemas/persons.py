from pydantic import BaseModel, Field

from typing import Optional

from database.schemas.person_scales import PersonScalesRead


# ----- базовые -----
class PersonBase(BaseModel):
    fio: str
    age: int
    height: int
    weight: int
    gender: bool  # False=муж, True=жен


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    fio: Optional[str] = None
    age: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    gender: Optional[bool] = None  # False=муж, True=жен


class PersonRead(PersonBase):
    id: int
    scales: Optional[PersonScalesRead] = None

    class Config:
        from_attributes = True
