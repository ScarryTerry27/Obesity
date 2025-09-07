from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from database.models import SliceT7


class SliceT7Repository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_slices_id(self, slices_id: int) -> SliceT7 | None:
        stmt = select(SliceT7).where(SliceT7.slices_id == slices_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: SliceT7) -> SliceT7:
        self.session.add(obj)
        return obj

    def update_fields(self, obj: SliceT7, **fields) -> SliceT7:
        for k, v in fields.items():
            if v is not None:
                setattr(obj, k, v)
        return obj

    def delete_by_slices_id(self, slices_id: int) -> int:
        stmt = delete(SliceT7).where(SliceT7.slices_id == slices_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0

