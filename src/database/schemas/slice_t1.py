from __future__ import annotations

from datetime import date as Date, time as Time
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SliceT1Input(BaseModel):
    date: Optional[Date] = None
    time: Optional[Time] = None
    rr_spont: Optional[float] = None
    heart_rate: Optional[float] = None
    sbp: Optional[float] = None
    dbp: Optional[float] = None
    map: Optional[float] = None
    spo2: Optional[float] = None
    urine_ml_per_h: Optional[float] = None
    hemoglobin: Optional[float] = None
    stroke_volume: Optional[float] = None
    cardiac_index: Optional[float] = None
    svri: Optional[float] = None
    cao: Optional[float] = None
    do2: Optional[float] = None
    vbd: Optional[float] = None
    fio2: Optional[float] = None
    uzl_score: Optional[float] = None
    ph_arterial: Optional[float] = None
    be_arterial: Optional[float] = None
    hco3_arterial: Optional[float] = None
    lactate_arterial: Optional[float] = None
    pao2: Optional[float] = None
    pao2_fio2: Optional[float] = None
    paco2: Optional[float] = None
    sao2: Optional[float] = None
    polo: Optional[bool] = None
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


class SliceT1Read(SliceT1Input):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slices_id: int
