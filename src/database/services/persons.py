from datetime import date
from typing import List

from sqlalchemy.orm import Session
from database.models import Person
from database.repositories.persons import PersonsRepository
from database.schemas.persons import PersonCreate, PersonRead, PersonUpdate
from database.services.person_scales import PersonScalesService
from database.services.person_slices import PersonSlicesService
from database.services.utils import NotFoundError


class PersonsService:
    """Бизнес-логика и транзакции."""

    def __init__(self, session: Session):
        self.repo = PersonsRepository(session)
        self.session = session

    def create_person(self, data: PersonCreate) -> PersonRead:
        person = Person(**data.model_dump(exclude_none=True))
        self.repo.add(person)
        self.session.commit()
        self.session.refresh(person)
        return PersonRead.model_validate(person)

    def get_person(self, person_id: int) -> PersonRead:
        person = self.repo.get(person_id)
        if not person:
            raise NotFoundError(...)
        out = PersonRead.model_validate(person)
        try:
            out.scales = PersonScalesService(self.session).get(person_id)
        except NotFoundError:
            out.scales = None

        try:
            out.slices = PersonSlicesService(self.session).get(person_id)
        except NotFoundError:
            out.slices = None
        return out

    def list_persons(self, limit: int = 100, offset: int = 0) -> list[PersonRead]:
        persons = self.repo.list(limit=limit, offset=offset)
        return [PersonRead.model_validate(p) for p in persons]

    def update_person(self, person_id: int, data: PersonUpdate) -> PersonRead:
        person = self.repo.get(person_id)
        if not person:
            raise NotFoundError(f"Person #{person_id} not found")
        self.repo.update_fields(person, **data.model_dump(exclude_unset=True))
        self.session.commit()
        self.session.refresh(person)
        return PersonRead.model_validate(person)

    def delete_person(self, person_id: int) -> bool:
        affected = self.repo.delete(person_id)
        self.session.commit()
        if affected == 0:
            raise NotFoundError(f"Person #{person_id} not found")
        return True

    def search_persons(
        self,
        last_name: str | None = None,
        first_name: str | None = None,
        patronymic: str | None = None,
        age: int | None = None,
        card_number: str | None = None,
        inclusion_date: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[PersonRead]:
        persons = self.repo.search(
            last_name=last_name,
            first_name=first_name,
            patronymic=patronymic,
            age=age,
            card_number=card_number,
            inclusion_date=inclusion_date,
            limit=limit,
            offset=offset,
        )
        return [PersonRead.model_validate(p) for p in persons]
