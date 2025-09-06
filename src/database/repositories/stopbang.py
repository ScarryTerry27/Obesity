from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from database.models import StopBangResult


class StopBangRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_scales_id(self, scales_id: int) -> StopBangResult | None:
        stmt = select(StopBangResult).where(StopBangResult.scales_id == scales_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: StopBangResult) -> StopBangResult:
        self.session.add(obj)
        return obj

    def delete_by_scales_id(self, scales_id: int) -> int:
        stmt = delete(StopBangResult).where(StopBangResult.scales_id == scales_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0
