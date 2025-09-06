from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class SobaBase(BaseModel):
    poor_functional_status: bool = False
    ekg_changes: bool = False
    uncontrolled_htn_ihd: bool = False
    spo2_room_air_lt_94: bool = False
    hypercapnia_co2_gt_28: bool = False
    vte_history: bool = False

    stopbang_score_cached: Optional[int] = Field(default=None)
    stopbang_risk_cached: Optional[int] = Field(default=None)


class SobaCreate(SobaBase):
    pass


class SobaUpdate(BaseModel):
    poor_functional_status: Optional[bool] = None
    ekg_changes: Optional[bool] = None
    uncontrolled_htn_ihd: Optional[bool] = None
    spo2_room_air_lt_94: Optional[bool] = None
    hypercapnia_co2_gt_28: Optional[bool] = None
    vte_history: Optional[bool] = None
    stopbang_score_cached: Optional[int] = None
    stopbang_risk_cached: Optional[int] = None


class SobaRead(SobaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    scales_id: int
