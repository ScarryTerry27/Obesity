from sqlalchemy.orm import Session

from database.models import LeeRcriResult, PersonScales
from database.repositories.lee import LeeRcriRepository
from database.repositories.person_scales import PersonScalesRepository
from database.schemas.lee import LeeRcriInput, LeeRcriUpdate, LeeRcriRead
from database.services.utils import NotFoundError


def _score_to_risk_percent(score: int) -> float:
    # по твоей таблице:
    # 0 → 0.4%, 1 → 0.9%, 2 → 7%, ≥3 → 11%
    if score <= 0:
        return 0.4
    if score == 1:
        return 0.9
    if score == 2:
        return 7.0
    return 11.0


class LeeRcriService:
    """Upsert/get/clear RCRI, синхронизация флага в PersonScales."""

    def __init__(self, session: Session):
        self.session = session
        self.repo = LeeRcriRepository(session)
        self.ps_repo = PersonScalesRepository(session)

    def _get_or_create_ps(self, person_id: int) -> PersonScales:
        ps = self.ps_repo.get_by_person_id(person_id)
        if ps is None:
            ps = PersonScales(person_id=person_id)
            self.ps_repo.add(ps)
            self.session.flush()
        return ps

    def _apply_creatinine_logic(self, obj: LeeRcriResult,
                                creatinine_umol_l: float | None,
                                creatinine_flag: bool | None):
        if creatinine_umol_l is not None:
            obj.creatinine_umol_l = float(creatinine_umol_l)
            obj.creatinine_gt_180_umol_l = bool(creatinine_umol_l > 180.0)
        elif creatinine_flag is not None:
            obj.creatinine_gt_180_umol_l = bool(creatinine_flag)
        # если ни того, ни другого — оставляем как есть

    def _recalc_totals(self, obj: LeeRcriResult):
        obj.total_score = sum([
            bool(obj.high_risk_surgery),
            bool(obj.ischemic_heart_disease),
            bool(obj.congestive_heart_failure),
            bool(obj.cerebrovascular_disease),
            bool(obj.diabetes_on_insulin),
            bool(obj.creatinine_gt_180_umol_l),
        ])
        obj.risk_percent = _score_to_risk_percent(obj.total_score)

    def upsert_result(self, person_id: int, data: LeeRcriInput | LeeRcriUpdate) -> LeeRcriRead:
        ps = self._get_or_create_ps(person_id)
        res = self.repo.get_by_scales_id(ps.id)

        payload = data.model_dump(exclude_unset=True)

        if res is None:
            res = LeeRcriResult(scales_id=ps.id)
            self.repo.add(res)

        # обновляем бинарные поля, если пришли
        for f in ("high_risk_surgery",
                  "ischemic_heart_disease",
                  "congestive_heart_failure",
                  "cerebrovascular_disease",
                  "diabetes_on_insulin"):
            if f in payload:
                setattr(res, f, bool(payload[f]))

        # креатинин — либо «сырое» значение, либо флаг
        self._apply_creatinine_logic(
            res,
            payload.get("creatinine_umol_l"),
            payload.get("creatinine_gt_180_umol_l"),
        )

        # пересчёт
        self._recalc_totals(res)

        # флаг заполнения
        self.ps_repo.update_fields(ps, lee_rcri_filled=True)

        self.session.commit()
        self.session.refresh(res)
        return LeeRcriRead.model_validate(res)

    def get_result(self, person_id: int) -> LeeRcriRead:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        res = self.repo.get_by_scales_id(ps.id)
        if not res:
            raise NotFoundError("LeeRcriResult not found")
        return LeeRcriRead.model_validate(res)

    def clear_result(self, person_id: int) -> bool:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        affected = self.repo.delete_by_scales_id(ps.id)
        if affected:
            self.ps_repo.update_fields(ps, lee_rcri_filled=False)
            self.session.commit()
            return True
        return False
