from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CapriniBase(BaseModel):
    # Сырые (опционально, для автосчёта возраста/ИМТ)
    age_years: Optional[int] = Field(default=None, ge=0, le=130)
    height_cm: Optional[float] = Field(default=None, ge=80, le=250)
    weight_kg: Optional[float] = Field(default=None, ge=20, le=400)

    # Категории возраста (если хочешь выставлять напрямую)
    age_41_60: bool = False
    age_61_74: bool = False
    age_ge_75: bool = False

    # ИМТ
    bmi_gt_25: bool = False

    # +1
    leg_swelling_now: bool = False
    varicose_veins: bool = False
    sepsis_lt_1m: bool = False
    severe_lung_disease_lt_1m: bool = False
    ocp_or_hrt: bool = False
    pregnant_or_postpartum_lt_1m: bool = False
    adverse_pregnancy_history: bool = False
    acute_mi: bool = False
    chf_now_or_lt_1m: bool = False
    bed_rest: bool = False
    ibd_history: bool = False
    copd: bool = False
    minor_surgery: bool = False
    additional_risk_factor: bool = False

    # +2
    bed_rest_gt_72h: bool = False
    major_surgery_lt_1m: bool = False
    cancer_current_or_past: bool = False
    limb_immobilization_lt_1m: bool = False
    central_venous_catheter: bool = False
    arthroscopic_surgery: bool = False
    laparoscopy_gt_60m: bool = False
    major_surgery_gt_45m: bool = False

    # +3
    personal_vte_history: bool = False
    factor_v_leiden: bool = False
    prothrombin_20210a: bool = False
    lupus_anticoagulant: bool = False
    family_vte_history: bool = False
    hyperhomocysteinemia: bool = False
    hit: bool = False
    anticardiolipin_antibodies: bool = False
    other_thrombophilia: bool = False

    # +5
    stroke_lt_1m: bool = False
    spinal_cord_injury_paralysis_lt_1m: bool = False
    multiple_trauma_lt_1m: bool = False
    major_joint_replacement: bool = False
    fracture_pelvis_or_limb: bool = False


class CapriniInput(CapriniBase):
    pass


class CapriniUpdate(BaseModel):
    # Всё опционально для частичного апдейта
    age_years: Optional[int] = Field(default=None, ge=0, le=130)
    height_cm: Optional[float] = Field(default=None, ge=80, le=250)
    weight_kg: Optional[float] = Field(default=None, ge=20, le=400)

    age_41_60: Optional[bool] = None
    age_61_74: Optional[bool] = None
    age_ge_75: Optional[bool] = None
    bmi_gt_25: Optional[bool] = None

    leg_swelling_now: Optional[bool] = None
    varicose_veins: Optional[bool] = None
    sepsis_lt_1m: Optional[bool] = None
    severe_lung_disease_lt_1m: Optional[bool] = None
    ocp_or_hrt: Optional[bool] = None
    pregnant_or_postpartum_lt_1m: Optional[bool] = None
    adverse_pregnancy_history: Optional[bool] = None
    acute_mi: Optional[bool] = None
    chf_now_or_lt_1m: Optional[bool] = None
    bed_rest: Optional[bool] = None
    ibd_history: Optional[bool] = None
    copd: Optional[bool] = None
    minor_surgery: Optional[bool] = None
    additional_risk_factor: Optional[bool] = None

    bed_rest_gt_72h: Optional[bool] = None
    major_surgery_lt_1m: Optional[bool] = None
    cancer_current_or_past: Optional[bool] = None
    limb_immobilization_lt_1m: Optional[bool] = None
    central_venous_catheter: Optional[bool] = None
    arthroscopic_surgery: Optional[bool] = None
    laparoscopy_gt_60m: Optional[bool] = None
    major_surgery_gt_45m: Optional[bool] = None

    personal_vte_history: Optional[bool] = None
    factor_v_leiden: Optional[bool] = None
    prothrombin_20210a: Optional[bool] = None
    lupus_anticoagulant: Optional[bool] = None
    family_vte_history: Optional[bool] = None
    hyperhomocysteinemia: Optional[bool] = None
    hit: Optional[bool] = None
    anticardiolipin_antibodies: Optional[bool] = None
    other_thrombophilia: Optional[bool] = None

    stroke_lt_1m: Optional[bool] = None
    spinal_cord_injury_paralysis_lt_1m: Optional[bool] = None
    multiple_trauma_lt_1m: Optional[bool] = None
    major_joint_replacement: Optional[bool] = None
    fracture_pelvis_or_limb: Optional[bool] = None


class CapriniRead(CapriniBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scales_id: int
    bmi_value: Optional[float] = None

    total_score: int
    risk_level: int  # 0=оч. низкий, 1=низкий, 2=умеренный, 3=высокий
