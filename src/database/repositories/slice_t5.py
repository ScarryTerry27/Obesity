from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database.models import SliceT5


class SliceT5Repository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_slices_id(self, slices_id: int) -> SliceT5 | None:
        stmt = select(SliceT5).where(SliceT5.slices_id == slices_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: SliceT5) -> SliceT5:
        self.session.add(obj)
        return obj

    def update_fields(self, obj: SliceT5, **fields) -> SliceT5:
        for k, v in fields.items():
            if v is not None:
                setattr(obj, k, v)
        return obj

    def delete_by_slices_id(self, slices_id: int) -> int:
        stmt = delete(SliceT5).where(SliceT5.slices_id == slices_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0
