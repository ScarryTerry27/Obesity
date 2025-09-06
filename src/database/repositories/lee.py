from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from typing import Optional

from database.models import LeeRcriResult


class LeeRcriRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_scales_id(self, scales_id: int) -> Optional[LeeRcriResult]:
        stmt = select(LeeRcriResult).where(LeeRcriResult.scales_id == scales_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: LeeRcriResult) -> LeeRcriResult:
        self.session.add(obj)
        return obj

    def update_fields(self, obj: LeeRcriResult, **fields) -> LeeRcriResult:
        for k, v in fields.items():
            if v is not None:
                setattr(obj, k, v)
        return obj

    def delete_by_scales_id(self, scales_id: int) -> int:
        stmt = delete(LeeRcriResult).where(LeeRcriResult.scales_id == scales_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0
