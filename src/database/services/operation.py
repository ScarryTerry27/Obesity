from sqlalchemy.orm import Session

from database.models import OperationData
from database.repositories.operation import OperationDataRepository
from database.schemas.operation import OperationDataInput, OperationDataRead


class OperationDataService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = OperationDataRepository(session)

    def add_measure(self, person_id: int, data: OperationDataInput) -> OperationDataRead:
        obj = OperationData(person_id=person_id, **data.model_dump())
        self.repo.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return OperationDataRead.model_validate(obj)

    def list_measures(self, person_id: int) -> list[OperationDataRead]:
        objs = self.repo.list_for_person(person_id)
        return [OperationDataRead.model_validate(o) for o in objs]

    def clear_person(self, person_id: int) -> int:
        count = self.repo.delete_for_person(person_id)
        self.session.commit()
        return count
