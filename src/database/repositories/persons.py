from datetime import date
from typing import Sequence

from sqlalchemy import select, delete, and_
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

    def search(
        self,
        last_name: str | None = None,
        first_name: str | None = None,
        patronymic: str | None = None,
        age: int | None = None,
        card_number: str | None = None,
        inclusion_date: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Person]:
        """Поиск по нескольким полям."""
        stmt = select(Person)
        conditions = []
        if last_name:
            conditions.append(Person.last_name.ilike(f"%{last_name}%"))
        if first_name:
            conditions.append(Person.first_name.ilike(f"%{first_name}%"))
        if patronymic:
            conditions.append(Person.patronymic.ilike(f"%{patronymic}%"))
        if card_number:
            conditions.append(Person.card_number.ilike(f"%{card_number}%"))
        if inclusion_date:
            conditions.append(Person.inclusion_date == inclusion_date)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = (
            stmt.order_by(Person.last_name.asc(), Person.first_name.asc())
            .offset(offset)
            .limit(limit)
        )
        persons = self.session.execute(stmt).scalars().all()
        if age is not None:
            persons = [p for p in persons if p.age == age]
        return persons
