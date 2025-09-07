from sqlalchemy.orm import Session

from database.models import PersonSlices
from database.repositories.person_slices import PersonSlicesRepository
from database.schemas.person_slices import PersonSlicesRead, PersonSlicesUpdate
from database.services.utils import NotFoundError


class PersonSlicesService:
    """Business logic for PersonSlices."""

    def __init__(self, session: Session):
        self.session = session
        self.repo = PersonSlicesRepository(session)

    def _ensure(self, person_id: int) -> PersonSlices:
        ps = self.repo.get_by_person_id(person_id)
        if ps is None:
            ps = PersonSlices(person_id=person_id)
            self.repo.add(ps)
            self.session.flush()
        return ps

    def get(self, person_id: int) -> PersonSlicesRead:
        ps = self.repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError(f"PersonSlices for person #{person_id} not found")
        return PersonSlicesRead.model_validate(ps)

    def ensure(self, person_id: int) -> PersonSlicesRead:
        ps = self._ensure(person_id)
        self.session.commit()
        return PersonSlicesRead.model_validate(ps)

    def update(self, person_id: int, data: PersonSlicesUpdate) -> PersonSlicesRead:
        ps = self._ensure(person_id)
        self.repo.update_fields(ps, **data.model_dump(exclude_unset=True))
        self.session.commit()
        self.session.refresh(ps)
        return PersonSlicesRead.model_validate(ps)

    def set_flag(self, person_id: int, slice_name: str, value: bool) -> PersonSlicesRead:
        allowed = {f"t{i}_filled" for i in range(13)}
        if slice_name not in allowed:
            raise ValueError(f"Unknown slice flag: {slice_name}")
        ps = self._ensure(person_id)
        setattr(ps, slice_name, bool(value))
        self.session.commit()
        self.session.refresh(ps)
        return PersonSlicesRead.model_validate(ps)

    def delete(self, person_id: int) -> bool:
        affected = self.repo.delete_by_person_id(person_id)
        self.session.commit()
        if affected == 0:
            raise NotFoundError(f"PersonSlices for person #{person_id} not found")
        return True
