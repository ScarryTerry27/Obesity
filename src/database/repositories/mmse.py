from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from database.models import MMSEResult


class MMSERepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_scales_and_time(self, scales_id: int, timepoint: int) -> MMSEResult | None:
        stmt = select(MMSEResult).where(
            MMSEResult.scales_id == scales_id,
            MMSEResult.timepoint == timepoint,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: MMSEResult) -> MMSEResult:
        self.session.add(obj)
        return obj

    def delete_by_scales_and_time(self, scales_id: int, timepoint: int) -> int:
        stmt = delete(MMSEResult).where(
            MMSEResult.scales_id == scales_id,
            MMSEResult.timepoint == timepoint,
        )
        res = self.session.execute(stmt)
        return res.rowcount or 0
