from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database.models import SliceT0


class SliceT0Repository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_slices_id(self, slices_id: int) -> SliceT0 | None:
        stmt = select(SliceT0).where(SliceT0.slices_id == slices_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: SliceT0) -> SliceT0:
        self.session.add(obj)
        return obj

    def update_fields(self, obj: SliceT0, **fields) -> SliceT0:
        for k, v in fields.items():
            if v is not None:
                setattr(obj, k, v)
        return obj

    def delete_by_slices_id(self, slices_id: int) -> int:
        stmt = delete(SliceT0).where(SliceT0.slices_id == slices_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0
