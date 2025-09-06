from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from database.models import CapriniResult


class CapriniRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_scales_id(self, scales_id: int) -> CapriniResult | None:
        stmt = select(CapriniResult).where(CapriniResult.scales_id == scales_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: CapriniResult) -> CapriniResult:
        self.session.add(obj)
        return obj

    def update_fields(self, obj: CapriniResult, **fields) -> CapriniResult:
        for k, v in fields.items():
            if v is not None:
                setattr(obj, k, v)
        return obj

    def delete_by_scales_id(self, scales_id: int) -> int:
        stmt = delete(CapriniResult).where(CapriniResult.scales_id == scales_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0
