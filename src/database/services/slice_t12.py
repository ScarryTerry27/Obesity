from sqlalchemy.orm import Session

from database.models import PersonSlices, SliceT12
from database.repositories.person_slices import PersonSlicesRepository
from database.repositories.slice_t12 import SliceT12Repository
from database.schemas.slice_t12 import SliceT12Input, SliceT12Read
from database.services.utils import NotFoundError


class SliceT12Service:
    """CRUD for slice T12 values with flag management."""

    def __init__(self, session: Session):
        self.session = session
        self.ps_repo = PersonSlicesRepository(session)
        self.repo = SliceT12Repository(session)

    def _get_or_create_ps(self, person_id: int) -> PersonSlices:
        ps = self.ps_repo.get_by_person_id(person_id)
        if ps is None:
            ps = PersonSlices(person_id=person_id)
            self.ps_repo.add(ps)
            self.session.flush()
        return ps

    def upsert(self, person_id: int, data: SliceT12Input) -> SliceT12Read:
        ps = self._get_or_create_ps(person_id)
        obj = self.repo.get_by_slices_id(ps.id)
        if obj is None:
            obj = SliceT12(slices_id=ps.id)
            self.repo.add(obj)
        self.repo.update_fields(obj, **data.model_dump(exclude_unset=True))
        self.ps_repo.update_fields(ps, t12_filled=True)
        self.session.commit()
        self.session.refresh(obj)
        self.session.refresh(ps)
        return SliceT12Read.model_validate(obj)

    def get(self, person_id: int) -> SliceT12Read:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonSlices not found")
        obj = self.repo.get_by_slices_id(ps.id)
        if not obj:
            raise NotFoundError("SliceT12 not found")
        return SliceT12Read.model_validate(obj)

    def delete(self, person_id: int) -> bool:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonSlices not found")
        affected = self.repo.delete_by_slices_id(ps.id)
        if affected:
            self.ps_repo.update_fields(ps, t12_filled=False)
        self.session.commit()
        return bool(affected)
