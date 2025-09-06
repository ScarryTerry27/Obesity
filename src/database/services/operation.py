from sqlalchemy.orm import Session

from database.models import OperationData
from database.repositories.operation import OperationDataRepository
from database.schemas.operation import OperationPointInput, OperationPointRead


class OperationDataService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = OperationDataRepository(session)

    def save_point(self, person_id: int, data: OperationPointInput) -> OperationPointRead:
        obj = OperationData(person_id=person_id, **data.model_dump())
        obj = self.repo.upsert(obj)
        self.session.commit()
        self.session.refresh(obj)
        return OperationPointRead.model_validate(obj)

    def list_points(self, person_id: int) -> list[OperationPointRead]:
        objs = self.repo.list_for_person(person_id)
        return [OperationPointRead.model_validate(o) for o in objs]

    def clear_person(self, person_id: int) -> int:
        count = self.repo.delete_for_person(person_id)
        self.session.commit()
        return count
