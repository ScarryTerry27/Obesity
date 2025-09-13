from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from database.models import Qor15Result


class Qor15Repository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_scales_id(self, scales_id: int) -> Qor15Result | None:
        stmt = select(Qor15Result).where(Qor15Result.scales_id == scales_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: Qor15Result) -> Qor15Result:
        self.session.add(obj)
        return obj

    def delete_by_scales_id(self, scales_id: int) -> int:
        stmt = delete(Qor15Result).where(Qor15Result.scales_id == scales_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0
