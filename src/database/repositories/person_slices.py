from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database.models import PersonSlices


class PersonSlicesRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, slices_id: int) -> PersonSlices | None:
        stmt = select(PersonSlices).where(PersonSlices.id == slices_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_person_id(self, person_id: int) -> PersonSlices | None:
        stmt = select(PersonSlices).where(PersonSlices.person_id == person_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, ps: PersonSlices) -> PersonSlices:
        self.session.add(ps)
        return ps

    def get_or_create_for_person(self, person_id: int) -> PersonSlices:
        ps = self.get_by_person_id(person_id)
        if ps is None:
            ps = PersonSlices(person_id=person_id)
            self.session.add(ps)
            self.session.flush()
        return ps

    def update_fields(self, ps: PersonSlices, **fields) -> PersonSlices:
        for k, v in fields.items():
            if v is not None:
                setattr(ps, k, v)
        return ps

    def delete_by_person_id(self, person_id: int) -> int:
        stmt = delete(PersonSlices).where(PersonSlices.person_id == person_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0
