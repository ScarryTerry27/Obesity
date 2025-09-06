from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from database.models import OperationData


class OperationDataRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_for_person(self, person_id: int) -> list[OperationData]:
        stmt = select(OperationData).where(OperationData.person_id == person_id)
        return list(self.session.execute(stmt).scalars().all())

    def add(self, obj: OperationData) -> OperationData:
        self.session.add(obj)
        return obj

    def delete_for_person(self, person_id: int) -> int:
        stmt = delete(OperationData).where(OperationData.person_id == person_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0
