from sqlalchemy.orm import Session

from database.models import PersonScales, Qor15Result
from database.repositories.person_scales import PersonScalesRepository
from database.repositories.qor15 import Qor15Repository
from database.schemas.qor15 import Qor15Input, Qor15Read
from database.services.utils import NotFoundError


class Qor15Service:
    """Upsert/get/clear QoR-15 and update flag in PersonScales."""

    def __init__(self, session: Session):
        self.session = session
        self.ps_repo = PersonScalesRepository(session)
        self.repo = Qor15Repository(session)

    def _get_or_create_ps(self, person_id: int) -> PersonScales:
        return self.ps_repo.get_or_create_for_person(person_id)

    def upsert_result(self, person_id: int, data: Qor15Input) -> Qor15Read:
        ps = self._get_or_create_ps(person_id)
        res = self.repo.get_by_scales_id(ps.id)
        if res is None:
            res = Qor15Result(scales_id=ps.id)
            self.repo.add(res)

        for i in range(1, 16):
            setattr(res, f"q{i}", int(getattr(data, f"q{i}")))
        res.total_score = sum(getattr(res, f"q{i}") for i in range(1, 16))

        self.ps_repo.update_fields(ps, qor15_filled=True)

        self.session.commit()
        self.session.refresh(res)
        self.session.refresh(ps)
        return Qor15Read.model_validate(res)

    def clear_result(self, person_id: int) -> bool:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        affected = self.repo.delete_by_scales_id(ps.id)
        if affected:
            self.ps_repo.update_fields(ps, qor15_filled=False)
        self.session.commit()
        return bool(affected)

    def get_result(self, person_id: int) -> Qor15Read:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        res = self.repo.get_by_scales_id(ps.id)
        if not res:
            raise NotFoundError("Qor15Result not found")
        return Qor15Read.model_validate(res)
