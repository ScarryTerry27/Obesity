from __future__ import annotations

# Aliased datetime imports to avoid name collisions with field names
from datetime import date as Date, time as Time
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SliceT0Input(BaseModel):
    date: Optional[Date] = None
    time: Optional[Time] = None
    rr_spont: Optional[float] = None
    fev1: Optional[float] = None
    fvc: Optional[float] = None
    frc: Optional[float] = None
    tlc: Optional[float] = None
    rv: Optional[float] = None
    fev1_fvc: Optional[float] = None
    pef: Optional[float] = None
    mef25: Optional[float] = None
    mef50: Optional[float] = None
    mef75: Optional[float] = None
    fef25_75: Optional[float] = None
    heart_rate: Optional[float] = None
    sbp: Optional[float] = None
    dbp: Optional[float] = None
    map: Optional[float] = None
    spo2: Optional[float] = None
    urine_ml_per_h: Optional[float] = None
    hemoglobin: Optional[float] = None
    neutrophils: Optional[float] = None
    lymphocytes: Optional[float] = None
    hematocrit: Optional[float] = None
    leukocytes: Optional[float] = None
    bands: Optional[float] = None
    albumin: Optional[float] = None
    creatinine: Optional[float] = None
    gfr: Optional[float] = None
    nlr: Optional[float] = None
    glucose: Optional[float] = None
    polo: Optional[bool] = None
    phrenic_syndrome: Optional[bool] = None
    phrenic_crsh: Optional[bool] = None
    aki: Optional[bool] = None
    complications: Optional[str] = None
    pain_nrs: Optional[float] = None
    pain_nrs_min: Optional[float] = None
    pain_nrs_max: Optional[float] = None
    nausea_vomiting: Optional[bool] = None
    aldrete_score: Optional[float] = None
    aldrete_time: Optional[float] = None
    t_activation: Optional[float] = None
    t_peristalsis: Optional[float] = None
    t_first_gas: Optional[float] = None
    opioid_consumption: Optional[float] = None
    urinary_catheter_pain: Optional[float] = None
    t_in_aro: Optional[float] = None
    t_intense_pain: Optional[float] = None
    t_restore_frc: Optional[float] = None
    t_restore_gfr: Optional[float] = None
    t_in_ward: Optional[float] = None
    qor15: Optional[float] = None
    satisfied: Optional[bool] = None


class SliceT0Read(SliceT0Input):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slices_id: int
