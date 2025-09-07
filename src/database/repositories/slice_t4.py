from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database.models import SliceT4


class SliceT4Repository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_slices_id(self, slices_id: int) -> SliceT4 | None:
        stmt = select(SliceT4).where(SliceT4.slices_id == slices_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: SliceT4) -> SliceT4:
        self.session.add(obj)
        return obj

    def update_fields(self, obj: SliceT4, **fields) -> SliceT4:
        for k, v in fields.items():
            if v is not None:
                setattr(obj, k, v)
        return obj

    def delete_by_slices_id(self, slices_id: int) -> int:
        stmt = delete(SliceT4).where(SliceT4.slices_id == slices_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0

