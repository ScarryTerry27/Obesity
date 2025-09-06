from sqlalchemy.orm import Session

from database.models import OperationData
from database.repositories.operation import OperationDataRepository
from database.schemas.operation import OperationPointInput, OperationPointRead
from database.parameters import PARAMETER_KEYS


class OperationDataService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = OperationDataRepository(session)

    def save_point(self, person_id: int, data: OperationPointInput) -> OperationPointRead:
        existing = self.repo.get_point(person_id, data.point)
        if existing:
            obj = existing
        else:
            obj = OperationData(person_id=person_id, point=data.point)
            self.repo.add(obj)
        for key in PARAMETER_KEYS:
            setattr(obj, key, data.data.get(key))
        self.session.commit()
        self.session.refresh(obj)
        return OperationPointRead.from_orm(obj)

    def list_points(self, person_id: int) -> list[OperationPointRead]:
        objs = self.repo.list_for_person(person_id)
        return [OperationPointRead.from_orm(o) for o in objs]

    def clear_person(self, person_id: int) -> int:
        count = self.repo.delete_for_person(person_id)
        self.session.commit()
        return count
