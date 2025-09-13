from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from database.models import LasVegasResult


class LasVegasRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_scales_id(self, scales_id: int) -> LasVegasResult | None:
        stmt = select(LasVegasResult).where(LasVegasResult.scales_id == scales_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: LasVegasResult) -> LasVegasResult:
        self.session.add(obj)
        return obj

    def delete_by_scales_id(self, scales_id: int) -> int:
        stmt = delete(LasVegasResult).where(LasVegasResult.scales_id == scales_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0
