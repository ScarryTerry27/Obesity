from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database.models import SliceT2


class SliceT2Repository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_slices_id(self, slices_id: int) -> SliceT2 | None:
        stmt = select(SliceT2).where(SliceT2.slices_id == slices_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: SliceT2) -> SliceT2:
        self.session.add(obj)
        return obj

    def update_fields(self, obj: SliceT2, **fields) -> SliceT2:
        for k, v in fields.items():
            if v is not None:
                setattr(obj, k, v)
        return obj

    def delete_by_slices_id(self, slices_id: int) -> int:
        stmt = delete(SliceT2).where(SliceT2.slices_id == slices_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0
