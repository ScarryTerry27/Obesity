from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from database.models import SliceT8


class SliceT8Repository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_slices_id(self, slices_id: int) -> SliceT8 | None:
        stmt = select(SliceT8).where(SliceT8.slices_id == slices_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: SliceT8) -> SliceT8:
        self.session.add(obj)
        return obj

    def update_fields(self, obj: SliceT8, **fields) -> SliceT8:
        for k, v in fields.items():
            if v is not None:
                setattr(obj, k, v)
        return obj

    def delete_by_slices_id(self, slices_id: int) -> int:
        stmt = delete(SliceT8).where(SliceT8.slices_id == slices_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0
