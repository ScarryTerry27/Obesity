from sqlalchemy.orm import Session

from database.models import PersonScales, StopBangResult
from database.repositories.person_scales import PersonScalesRepository
from database.repositories.stopbang import StopBangRepository
from database.schemas.stopbang import StopBangInput, StopBangRead
from database.services.utils import NotFoundError


def _risk_level(score: int) -> int:
    # часто используют:
    # 0–2 низкий, 3–4 умеренный, 5–8 высокий
    if score >= 5:
        return 2
    if score >= 3:
        return 1
    return 0


class StopBangService:
    """Upsert/get/clear STOP-BANG + установка флага в PersonScales."""

    def __init__(self, session: Session):
        self.session = session
        self.ps_repo = PersonScalesRepository(session)
        self.repo = StopBangRepository(session)

    def _get_or_create_ps(self, person_id: int) -> PersonScales:
        ps = self.ps_repo.get_by_person_id(person_id)
        if ps is None:
            ps = PersonScales(person_id=person_id)
            self.ps_repo.add(ps)
            self.session.flush()
        return ps

    def upsert_result(self, person_id: int, data: StopBangInput) -> StopBangRead:
        ps = self._get_or_create_ps(person_id)
        res = self.repo.get_by_scales_id(ps.id)
        if res is None:
            res = StopBangResult(scales_id=ps.id)
            self.repo.add(res)

        # 1) Локальные булевы флаги (никаких None):
        s_snoring = bool(data.s_snoring)
        t_tired_daytime = bool(data.t_tired_daytime)
        o_observed_apnea = bool(data.o_observed_apnea)
        p_hypertension = bool(data.p_hypertension)
        g_male = bool(data.g_male)

        b_bmi_ge_35 = bool(data.bmi_value >= 35.0)
        a_age_gt_50 = bool(data.age_years > 50)
        n_neck_gt_40 = bool(data.neck_circ_cm > 40.0)

        # 2) Записываем в модель (чтобы объект в сессии был консистентен):
        res.s_snoring = s_snoring
        res.t_tired_daytime = t_tired_daytime
        res.o_observed_apnea = o_observed_apnea
        res.p_hypertension = p_hypertension
        res.b_bmi_ge_35 = b_bmi_ge_35
        res.a_age_gt_50 = a_age_gt_50
        res.n_neck_gt_40 = n_neck_gt_40
        res.g_male = g_male

        res.bmi_value = float(data.bmi_value)
        res.age_years = int(data.age_years)
        res.neck_circ_cm = float(data.neck_circ_cm)

        # 3) Считаем баллы ТОЛЬКО из локальных булей (никаких None):
        flags = [s_snoring, t_tired_daytime, o_observed_apnea, p_hypertension,
                 b_bmi_ge_35, a_age_gt_50, n_neck_gt_40, g_male]
        res.total_score = sum(int(f) for f in flags)

        # 4) Риск
        res.risk_level = _risk_level(res.total_score)

        # 5) Верный флаг заполненности:
        self.ps_repo.update_fields(ps, stopbang_filled=True)

        self.session.commit()
        self.session.refresh(res)
        self.session.refresh(ps)
        return StopBangRead.model_validate(res)

    def clear_result(self, person_id: int) -> bool:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        affected = self.repo.delete_by_scales_id(ps.id)
        if affected:
            # ❗ тоже меняем на отдельный флаг
            self.ps_repo.update_fields(ps, stopbang_filled=False)
        self.session.commit()
        return bool(affected)

    def get_result(self, person_id: int) -> StopBangRead:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        res = self.repo.get_by_scales_id(ps.id)
        if not res:
            raise NotFoundError("StopBangResult not found")
        return StopBangRead.model_validate(res)
