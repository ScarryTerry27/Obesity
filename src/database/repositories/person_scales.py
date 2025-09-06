# database/repositories/person_scales.py
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from database.models import PersonScales


class PersonScalesRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, scales_id: int) -> PersonScales | None:
        stmt = select(PersonScales).where(PersonScales.id == scales_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_person_id(self, person_id: int) -> PersonScales | None:
        stmt = select(PersonScales).where(PersonScales.person_id == person_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, ps: PersonScales) -> PersonScales:
        self.session.add(ps)
        return ps

    def get_or_create_for_person(self, person_id: int) -> PersonScales:
        ps = self.get_by_person_id(person_id)
        if ps is None:
            ps = PersonScales(person_id=person_id)
            self.session.add(ps)
            # ВАЖНО: получить ps.id до использования как FK
            self.session.flush()
        return ps

    def update_fields(self, ps: PersonScales, **fields) -> PersonScales:
        for k, v in fields.items():
            if v is not None:
                setattr(ps, k, v)
        return ps

    def delete_by_person_id(self, person_id: int) -> int:
        stmt = delete(PersonScales).where(PersonScales.person_id == person_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0
