from sqlalchemy.orm import Session

from database.enums.ariscat import AriscatAge, AriscatSpO2, AriscatIncision, AriscatDuration, AriscatRespInfect, \
    AriscatAnemia, AriscatEmergency
from database.models import PersonScales, AriscatResult
from database.repositories.person_scales import PersonScalesRepository
from database.repositories.ariscat import AriscatRepository
from database.schemas.ariscat import AriscatInput, AriscatRead
from database.services.utils import NotFoundError


# --- маппинг raw → категория ---
def _age_cat(age: int) -> AriscatAge:
    if age <= 50:
        return AriscatAge.LE_50
    if age <= 80:
        return AriscatAge.BW_51_80
    return AriscatAge.GT_80


def _spo2_cat(spo2: int) -> AriscatSpO2:
    if spo2 >= 96:
        return AriscatSpO2.GE_96
    if spo2 >= 91:
        return AriscatSpO2.BW_91_95
    return AriscatSpO2.LE_90


def _incision_cat(code: str) -> AriscatIncision:
    if code == "upper_abd":
        return AriscatIncision.UPPER_ABD
    if code == "intrathoracic":
        return AriscatIncision.INTRATHORACIC
    return AriscatIncision.PERIPHERAL


def _duration_cat(mins: int) -> AriscatDuration:
    if mins < 120:
        return AriscatDuration.LT_2H
    if mins <= 180:
        return AriscatDuration.BW_2_3H
    return AriscatDuration.GT_3H


def _bool_cat(flag: bool, yes_enum, no_enum):
    return yes_enum if flag else no_enum


class AriscatService:
    """Бизнес-логика ARISCAT: upsert, get, расчёт баллов и установка флага filled."""

    def __init__(self, session: Session):
        self.session = session
        self.ps_repo = PersonScalesRepository(session)
        self.repo = AriscatRepository(session)

    def _get_or_create_ps(self, person_id: int) -> PersonScales:
        ps = self.ps_repo.get_by_person_id(person_id)
        if ps is None:
            ps = PersonScales(person_id=person_id)
            self.ps_repo.add(ps)
            self.session.flush()
        return ps

    def upsert_result(self, person_id: int, data: AriscatInput) -> AriscatRead:
        ps = self._get_or_create_ps(person_id)
        res = self.repo.get_by_scales_id(ps.id)
        if res is None:
            res = AriscatResult(scales_id=ps.id)
            self.repo.add(res)

        # категории
        res.cat_age = _age_cat(data.age_years)
        res.cat_spo2 = _spo2_cat(data.spo2_percent)
        res.cat_resp_inf = _bool_cat(data.had_resp_infection_last_month, AriscatRespInfect.YES, AriscatRespInfect.NO)
        res.cat_anemia = _bool_cat(data.has_anemia_hb_le_100, AriscatAnemia.YES, AriscatAnemia.NO)
        res.cat_incision = _incision_cat(data.incision)
        res.cat_duration = _duration_cat(data.duration_minutes)
        res.cat_emerg = _bool_cat(data.is_emergency, AriscatEmergency.YES, AriscatEmergency.NO)

        # сырые
        res.age_years = data.age_years
        res.spo2_percent = data.spo2_percent
        res.had_resp_infection_last_month = data.had_resp_infection_last_month
        res.has_anemia_hb_le_100 = data.has_anemia_hb_le_100
        res.incision_raw = data.incision
        res.duration_minutes = data.duration_minutes
        res.is_emergency = data.is_emergency

        # сумма баллов — просто сумма значений enum (мы закодировали веса в значениях)
        res.total_score = (
                res.cat_age.value
                + res.cat_spo2.value
                + res.cat_resp_inf.value
                + res.cat_anemia.value
                + res.cat_incision.value
                + res.cat_duration.value
                + res.cat_emerg.value
        )

        # отметить флаг заполнения
        self.ps_repo.update_fields(ps, ariscat_filled=True)

        self.session.commit()
        self.session.refresh(res)
        return AriscatRead.model_validate(res)

    def get_result(self, person_id: int) -> AriscatRead:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        res = self.repo.get_by_scales_id(ps.id)
        if not res:
            raise NotFoundError("AriscatResult not found")
        return AriscatRead.model_validate(res)

    def clear_result(self, person_id: int) -> bool:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        affected = self.repo.delete_by_scales_id(ps.id)
        if affected:
            self.ps_repo.update_fields(ps, ariscat_filled=False)
        self.session.commit()
        return bool(affected)
