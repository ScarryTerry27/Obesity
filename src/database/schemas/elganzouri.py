# schemas.py
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ElGanzouriInput(BaseModel):
    interincisor_cm: float = Field(..., ge=0, le=10)
    thyromental_cm: float = Field(..., ge=0, le=12)
    neck_ext_deg: float = Field(..., ge=0, le=150)
    weight_kg: float = Field(..., ge=20, le=400)
    mallampati_raw: int = Field(..., ge=1, le=4)  # I..IV как 1..4
    can_protrude: bool
    diff_hx: str  # 'Нет' | 'Недостоверно' | 'Определенно'


class ElGanzouriRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scales_id: int
    total_score: int

    # дублируем ключевые сохранённые «сырые» значения — удобно в UI
    interincisor_cm: float | None = None
    thyromental_cm: float | None = None
    neck_ext_deg: float | None = None
    weight_kg: float | None = None
    mallampati_raw: int | None = None


class ScalesStatusRead(BaseModel):
    filled: bool
    total_score: Optional[int] = None
