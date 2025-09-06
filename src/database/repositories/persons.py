from typing import Sequence

from sqlalchemy import select, delete, or_
from sqlalchemy.orm import Session

from database.models import Person


class PersonsRepository:
    """Чистый доступ к БД без бизнес-логики."""

    def __init__(self, session: Session):
        self.session = session

    # C
    def add(self, person: Person) -> Person:
        self.session.add(person)
        return person

    # R
    def get(self, person_id: int) -> Person | None:
        return self.session.get(Person, person_id)

    def list(self, limit: int = 100, offset: int = 0) -> Sequence[Person]:
        stmt = select(Person).offset(offset).limit(limit)
        return self.session.execute(stmt).scalars().all()

    # U
    def update_fields(self, person: Person, **fields) -> Person:
        for k, v in fields.items():
            if v is not None:
                setattr(person, k, v)
        return person

    # D
    def delete(self, person_id: int) -> int:
        stmt = delete(Person).where(Person.id == person_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0

    def search_by_fio(self, query: str, limit: int = 50, offset: int = 0) -> Sequence[Person]:
        """Ищет по подстроке в любом из полей ФИО (регистр не важен)."""
        q = (query or "").strip()
        if not q:
            return []
        stmt = (
            select(Person)
            .where(
                or_(
                    Person.last_name.ilike(f"%{q}%"),
                    Person.first_name.ilike(f"%{q}%"),
                    Person.patronymic.ilike(f"%{q}%"),
                )
            )
            .order_by(Person.last_name.asc(), Person.first_name.asc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()
