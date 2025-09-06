from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class LeeRcriInput(BaseModel):
    high_risk_surgery: bool
    ischemic_heart_disease: bool
    congestive_heart_failure: bool
    cerebrovascular_disease: bool
    diabetes_on_insulin: bool
    creatinine_gt_180_umol_l: Optional[bool] = None


class LeeRcriUpdate(BaseModel):
    high_risk_surgery: Optional[bool] = None
    ischemic_heart_disease: Optional[bool] = None
    congestive_heart_failure: Optional[bool] = None
    cerebrovascular_disease: Optional[bool] = None
    diabetes_on_insulin: Optional[bool] = None
    creatinine_gt_180_umol_l: Optional[bool] = None


class LeeRcriRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scales_id: int

    high_risk_surgery: bool
    ischemic_heart_disease: bool
    congestive_heart_failure: bool
    cerebrovascular_disease: bool
    diabetes_on_insulin: bool
    creatinine_gt_180_umol_l: bool
    total_score: int
    risk_percent: float
