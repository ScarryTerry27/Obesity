from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database.models import SliceT3


class SliceT3Repository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_slices_id(self, slices_id: int) -> SliceT3 | None:
        stmt = select(SliceT3).where(SliceT3.slices_id == slices_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: SliceT3) -> SliceT3:
        self.session.add(obj)
        return obj

    def update_fields(self, obj: SliceT3, **fields) -> SliceT3:
        for k, v in fields.items():
            if v is not None:
                setattr(obj, k, v)
        return obj

    def delete_by_slices_id(self, slices_id: int) -> int:
        stmt = delete(SliceT3).where(SliceT3.slices_id == slices_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0
