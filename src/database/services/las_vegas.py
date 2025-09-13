from sqlalchemy.orm import Session

from database.models import PersonScales, LasVegasResult
from database.repositories.person_scales import PersonScalesRepository
from database.repositories.las_vegas import LasVegasRepository
from database.schemas.las_vegas import LasVegasInput, LasVegasRead
from database.services.utils import NotFoundError


def _risk_level(score: int) -> int:
    if score >= 6:
        return 2
    if score >= 3:
        return 1
    return 0


class LasVegasService:
    def __init__(self, session: Session):
        self.session = session
        self.ps_repo = PersonScalesRepository(session)
        self.repo = LasVegasRepository(session)

    def _get_or_create_ps(self, person_id: int) -> PersonScales:
        ps = self.ps_repo.get_by_person_id(person_id)
        if ps is None:
            ps = PersonScales(person_id=person_id)
            self.ps_repo.add(ps)
            self.session.flush()
        return ps

    def upsert_result(self, person_id: int, data: LasVegasInput) -> LasVegasRead:
        ps = self._get_or_create_ps(person_id)
        res = self.repo.get_by_scales_id(ps.id)
        if res is None:
            res = LasVegasResult(scales_id=ps.id)
            self.repo.add(res)

        # assign fields
        res.age_years = int(data.age_years)
        res.asa_ps = int(data.asa_ps)
        res.preop_spo2 = int(data.preop_spo2)
        res.cancer = bool(data.cancer)
        res.osa = bool(data.osa)
        res.elective = bool(data.elective)
        res.duration_minutes = int(data.duration_minutes)
        res.supraglottic_device = bool(data.supraglottic_device)
        res.anesthesia_type = str(data.anesthesia_type)
        res.intraop_desaturation = bool(data.intraop_desaturation)
        res.vasoactive_drugs = bool(data.vasoactive_drugs)
        res.peep_cm_h2o = float(data.peep_cm_h2o)

        score = 0
        if data.age_years >= 67:
            score += 2
        elif data.age_years >= 47:
            score += 1
        if data.asa_ps >= 3:
            score += 1
        if data.preop_spo2 < 96:
            score += 1
        if data.cancer:
            score += 1
        if data.osa:
            score += 1
        if not data.elective:
            score += 1
        if data.duration_minutes >= 135:
            score += 1
        if data.supraglottic_device:
            score += 1
        if str(data.anesthesia_type).lower() != "balanced":
            score += 1
        if data.intraop_desaturation:
            score += 1
        if data.vasoactive_drugs:
            score += 1
        if data.peep_cm_h2o < 5:
            score += 1

        res.total_score = score
        res.risk_level = _risk_level(score)

        self.ps_repo.update_fields(ps, las_vegas_filled=True)
        self.session.commit()
        self.session.refresh(res)
        self.session.refresh(ps)
        return LasVegasRead.model_validate(res)

    def clear_result(self, person_id: int) -> bool:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        affected = self.repo.delete_by_scales_id(ps.id)
        if affected:
            self.ps_repo.update_fields(ps, las_vegas_filled=False)
        self.session.commit()
        return bool(affected)

    def get_result(self, person_id: int) -> LasVegasRead:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        res = self.repo.get_by_scales_id(ps.id)
        if not res:
            raise NotFoundError("LasVegasResult not found")
        return LasVegasRead.model_validate(res)
