from sqlalchemy.orm import Session

from database.models import PersonScales
from database.repositories.person_scales import PersonScalesRepository
from database.schemas.person_scales import PersonScalesRead, PersonScalesUpdate
from database.services.utils import NotFoundError


class PersonScalesService:
    """Бизнес-логика и транзакции для PersonScales."""

    def __init__(self, session: Session):
        self.session = session
        self.repo = PersonScalesRepository(session)

    def _ensure(self, person_id: int) -> PersonScales:
        """Получить или создать пустую запись статусов для пациента."""
        ps = self.repo.get_by_person_id(person_id)
        if ps is None:
            ps = PersonScales(person_id=person_id)
            self.repo.add(ps)
            self.session.flush()  # сразу получим id
        return ps

    # R
    def get(self, person_id: int) -> PersonScalesRead:
        ps = self.repo.get_by_person_id(person_id)
        if not ps:
            # по твоему стилю — NotFoundError
            raise NotFoundError(f"PersonScales for person #{person_id} not found")
        return PersonScalesRead.model_validate(ps)

    # C (idempotent create/ensure)
    def ensure(self, person_id: int) -> PersonScalesRead:
        ps = self._ensure(person_id)
        self.session.commit()
        return PersonScalesRead.model_validate(ps)

    # U
    def update(self, person_id: int, data: PersonScalesUpdate) -> PersonScalesRead:
        ps = self._ensure(person_id)
        self.repo.update_fields(ps, **data.model_dump(exclude_unset=True))
        self.session.commit()
        self.session.refresh(ps)
        return PersonScalesRead.model_validate(ps)

    # Удобные шорткаты по одной шкале (если нужно)
    def set_flag(self, person_id: int, scale_name: str, value: bool) -> PersonScalesRead:
        """
        scale_name: одно из
        ['el_ganzouri_filled','ariscat_filled','soba_stopbang_filled','lee_rcri_filled','caprini_filled','las_vegas_filled']
        """
        if scale_name not in {
            "el_ganzouri_filled", "ariscat_filled", "soba_stopbang_filled",
            "lee_rcri_filled", "caprini_filled", "las_vegas_filled"
        }:
            raise ValueError(f"Unknown scale flag: {scale_name}")

        ps = self._ensure(person_id)
        setattr(ps, scale_name, bool(value))
        self.session.commit()
        self.session.refresh(ps)
        return PersonScalesRead.model_validate(ps)

    # D (опционально — подчистить все статусы пациента)
    def delete(self, person_id: int) -> bool:
        affected = self.repo.delete_by_person_id(person_id)
        self.session.commit()
        if affected == 0:
            raise NotFoundError(f"PersonScales for person #{person_id} not found")
        return True
