from pydantic import BaseModel, ConfigDict


class LasVegasInput(BaseModel):
    age_years: int
    asa_ps: int
    preop_spo2: int
    cancer: bool
    osa: bool
    elective: bool
    duration_minutes: int
    supraglottic_device: bool
    anesthesia_type: str
    intraop_desaturation: bool
    vasoactive_drugs: bool
    peep_cm_h2o: float


class LasVegasRead(LasVegasInput):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scales_id: int
    total_score: int
    risk_level: int
