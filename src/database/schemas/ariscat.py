from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class AriscatInput(BaseModel):
    age_years: int = Field(..., ge=0, le=130)
    spo2_percent: int = Field(..., ge=50, le=100)
    had_resp_infection_last_month: bool
    has_anemia_hb_le_100: bool
    incision: str = Field(..., pattern="^(peripheral|upper_abd|intrathoracic)$")
    duration_minutes: int = Field(..., ge=0, le=24 * 60)
    is_emergency: bool


class AriscatRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scales_id: int
    total_score: int

    # вернём и сырые значения, чтобы подставлять по умолчанию в форму
    age_years: Optional[int] = None
    spo2_percent: Optional[int] = None
    had_resp_infection_last_month: Optional[bool] = None
    has_anemia_hb_le_100: Optional[bool] = None
    incision_raw: Optional[str] = None
    duration_minutes: Optional[int] = None
    is_emergency: Optional[bool] = None
