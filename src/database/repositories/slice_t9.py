from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from database.models import SliceT9


class SliceT9Repository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_slices_id(self, slices_id: int) -> SliceT9 | None:
        stmt = select(SliceT9).where(SliceT9.slices_id == slices_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: SliceT9) -> SliceT9:
        self.session.add(obj)
        return obj

    def update_fields(self, obj: SliceT9, **fields) -> SliceT9:
        for k, v in fields.items():
            if v is not None:
                setattr(obj, k, v)
        return obj

    def delete_by_slices_id(self, slices_id: int) -> int:
        stmt = delete(SliceT9).where(SliceT9.slices_id == slices_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0

