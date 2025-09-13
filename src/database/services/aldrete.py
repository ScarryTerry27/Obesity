from sqlalchemy.orm import Session

from database.models import PersonScales, AldreteResult
from database.repositories.person_scales import PersonScalesRepository
from database.repositories.aldrete import AldreteRepository
from database.schemas.aldrete import AldreteInput, AldreteRead
from database.services.utils import NotFoundError


class AldreteService:
    def __init__(self, session: Session):
        self.session = session
        self.ps_repo = PersonScalesRepository(session)
        self.repo = AldreteRepository(session)

    def _get_or_create_ps(self, person_id: int) -> PersonScales:
        ps = self.ps_repo.get_by_person_id(person_id)
        if ps is None:
            ps = PersonScales(person_id=person_id)
            self.ps_repo.add(ps)
            self.session.flush()
        return ps

    def upsert_result(self, person_id: int, data: AldreteInput) -> AldreteRead:
        ps = self._get_or_create_ps(person_id)
        res = self.repo.get_by_scales_id(ps.id)
        if res is None:
            res = AldreteResult(scales_id=ps.id)
            self.repo.add(res)

        res.activity_score = int(data.activity_score)
        res.respiration_score = int(data.respiration_score)
        res.pressure_score = int(data.pressure_score)
        res.consciousness_score = int(data.consciousness_score)
        res.spo2_score = int(data.spo2_score)
        res.total_score = (
            res.activity_score +
            res.respiration_score +
            res.pressure_score +
            res.consciousness_score +
            res.spo2_score
        )

        self.ps_repo.update_fields(ps, aldrete_filled=True)
        self.session.commit()
        self.session.refresh(res)
        self.session.refresh(ps)
        return AldreteRead.model_validate(res)

    def clear_result(self, person_id: int) -> bool:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        affected = self.repo.delete_by_scales_id(ps.id)
        if affected:
            self.ps_repo.update_fields(ps, aldrete_filled=False)
        self.session.commit()
        return bool(affected)

    def get_result(self, person_id: int) -> AldreteRead:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        res = self.repo.get_by_scales_id(ps.id)
        if not res:
            raise NotFoundError("AldreteResult not found")
        return AldreteRead.model_validate(res)
