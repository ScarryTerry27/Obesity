from pydantic import BaseModel, Field

from typing import Optional
from datetime import date

from database.enums.anesthesia import AnesthesiaType
from database.schemas.person_scales import PersonScalesRead
from database.schemas.person_slices import PersonSlicesRead


# ----- базовые -----
class PersonBase(BaseModel):
    card_number: Optional[str] = None
    anesthesia_type: Optional[AnesthesiaType] = None
    last_name: str
    first_name: str
    patronymic: Optional[str] = None
    birth_date: date
    inclusion_date: Optional[date] = None
    height: int
    weight: int
    gender: bool  # False=муж, True=жен


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    card_number: Optional[str] = None
    anesthesia_type: Optional[AnesthesiaType] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    patronymic: Optional[str] = None
    birth_date: Optional[date] = None
    inclusion_date: Optional[date] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    gender: Optional[bool] = None  # False=муж, True=жен


class PersonRead(PersonBase):
    id: int
    fio: str
    age: Optional[int] = None
    scales: Optional[PersonScalesRead] = None
    slices: Optional[PersonSlicesRead] = None

    class Config:
        from_attributes = True
