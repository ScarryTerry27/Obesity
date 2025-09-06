# database/services/caprini.py
from sqlalchemy.orm import Session
from database.models import PersonScales, CapriniResult
from database.repositories.person_scales import PersonScalesRepository
from database.repositories.caprini import CapriniRepository
from database.schemas.caprini import CapriniInput, CapriniUpdate, CapriniRead
from database.services.utils import NotFoundError


def _risk_band(total: int) -> int:
    # 0–1 = 0 (оч. низкий), 2 = 1 (низкий), 3–4 = 2 (умеренный), >=5 = 3 (высокий)
    if total >= 5:
        return 3
    if total >= 3:
        return 2
    if total == 2:
        return 1
    return 0


def _derive_age_flags(age_years: int | None) -> tuple[bool, bool, bool]:
    """Возвращает (41–60, 61–74, >=75)"""
    a1 = a2 = a3 = False
    if age_years is None:
        return a1, a2, a3
    if 41 <= age_years <= 60:
        a1 = True
    elif 61 <= age_years <= 74:
        a2 = True
    elif age_years >= 75:
        a3 = True
    return a1, a2, a3


def _derive_bmi_flag(height_cm: float | None, weight_kg: float | None) -> tuple[float | None, bool]:
    """Возвращает (bmi_value, bmi_gt_25)"""
    if not height_cm or not weight_kg:
        return None, False
    try:
        h_m = height_cm / 100.0
        if h_m <= 0:
            return None, False
        bmi = weight_kg / (h_m * h_m)
        return float(round(bmi, 1)), bmi > 25.0
    except Exception:
        return None, False


def _score_caprini(c: CapriniResult) -> int:
    s = 0
    # возраст
    s += 1 if c.age_41_60 else 0
    s += 2 if c.age_61_74 else 0
    s += 3 if c.age_ge_75 else 0
    # ИМТ
    s += 1 if c.bmi_gt_25 else 0

    # +1
    one_point = [
        c.leg_swelling_now, c.varicose_veins, c.sepsis_lt_1m, c.severe_lung_disease_lt_1m,
        c.ocp_or_hrt, c.pregnant_or_postpartum_lt_1m, c.adverse_pregnancy_history, c.acute_mi,
        c.chf_now_or_lt_1m, c.bed_rest, c.ibd_history, c.copd, c.minor_surgery,
        c.additional_risk_factor
    ]
    s += sum(1 for v in one_point if v)

    # +2
    two_point = [
        c.bed_rest_gt_72h, c.major_surgery_lt_1m, c.cancer_current_or_past, c.limb_immobilization_lt_1m,
        c.central_venous_catheter, c.arthroscopic_surgery, c.laparoscopy_gt_60m, c.major_surgery_gt_45m
    ]
    s += 2 * sum(1 for v in two_point if v)

    # +3
    three_point = [
        c.personal_vte_history, c.factor_v_leiden, c.prothrombin_20210a, c.lupus_anticoagulant,
        c.family_vte_history, c.hyperhomocysteinemia, c.hit, c.anticardiolipin_antibodies,
        c.other_thrombophilia
    ]
    s += 3 * sum(1 for v in three_point if v)

    # +5
    five_point = [
        c.stroke_lt_1m, c.spinal_cord_injury_paralysis_lt_1m, c.multiple_trauma_lt_1m,
        c.major_joint_replacement, c.fracture_pelvis_or_limb
    ]
    s += 5 * sum(1 for v in five_point if v)

    return s


class CapriniService:
    """Upsert/get/clear CAPRINI + флаг в PersonScales."""

    def __init__(self, session: Session):
        self.session = session
        self.ps_repo = PersonScalesRepository(session)
        self.repo = CapriniRepository(session)

    def _get_or_create_ps(self, person_id: int) -> PersonScales:
        ps = self.ps_repo.get_by_person_id(person_id)
        if ps is None:
            ps = PersonScales(person_id=person_id)
            self.ps_repo.add(ps)
            self.session.flush()
        return ps

    def upsert_result(self, person_id: int, data: CapriniInput | CapriniUpdate) -> CapriniRead:
        ps = self._get_or_create_ps(person_id)
        obj = self.repo.get_by_scales_id(ps.id)
        payload = data.model_dump(exclude_unset=True)

        if obj is None:
            obj = CapriniResult(scales_id=ps.id)
            self.repo.add(obj)

        # обновляем сырые поля, если пришли
        for fld in ("age_years", "height_cm", "weight_kg"):
            if fld in payload:
                setattr(obj, fld, payload[fld])

        # авто-вывод возраста/ИМТ в категории (если переданы сырые)
        if obj.age_years is not None:
            a1, a2, a3 = _derive_age_flags(obj.age_years)
            obj.age_41_60 = a1
            obj.age_61_74 = a2
            obj.age_ge_75 = a3

        bmi_value, bmi_flag = _derive_bmi_flag(obj.height_cm, obj.weight_kg)
        if bmi_value is not None:
            obj.bmi_value = bmi_value
            obj.bmi_gt_25 = bmi_flag

        # Обновим все булевые из payload (перекрывая автозначения, если пользователь задал напрямую)
        self.repo.update_fields(obj, **payload)

        # Пересчёт баллов и риска
        obj.total_score = _score_caprini(obj)
        obj.risk_level = _risk_band(obj.total_score)

        # флаг у пациента
        self.ps_repo.update_fields(ps, caprini_filled=True)

        self.session.commit()
        self.session.refresh(obj)
        return CapriniRead.model_validate(obj)

    def get_result(self, person_id: int) -> CapriniRead:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        obj = self.repo.get_by_scales_id(ps.id)
        if not obj:
            raise NotFoundError("Caprini not found")
        return CapriniRead.model_validate(obj)

    def clear_result(self, person_id: int) -> bool:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        affected = self.repo.delete_by_scales_id(ps.id)
        if affected:
            self.ps_repo.update_fields(ps, caprini_filled=False)
            self.session.commit()
            return True
        return False
