from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class StopBangInput(BaseModel):
    # то, что вводит UI
    s_snoring: bool
    t_tired_daytime: bool
    o_observed_apnea: bool
    p_hypertension: bool
    g_male: bool

    # численные поля для вычисления B, A, N
    age_years: int = Field(..., ge=0, le=130)
    bmi_value: float = Field(..., ge=5, le=120)
    neck_circ_cm: float = Field(..., ge=10, le=80)


class StopBangRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scales_id: int
    # булевы признаки
    s_snoring: bool
    t_tired_daytime: bool
    o_observed_apnea: bool
    p_hypertension: bool
    b_bmi_ge_35: bool
    a_age_gt_50: bool
    n_neck_gt_40: bool
    g_male: bool

    # численные
    bmi_value: Optional[float] = None
    age_years: Optional[int] = None
    neck_circ_cm: Optional[float] = None

    total_score: int
    risk_level: int
   