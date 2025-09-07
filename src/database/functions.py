from database.db import SessionLocal
from database.schemas.ariscat import AriscatInput, AriscatRead
from database.schemas.caprini import CapriniRead, CapriniInput
from database.schemas.elganzouri import ElGanzouriRead, ElGanzouriInput
from database.schemas.lee import LeeRcriRead, LeeRcriInput, LeeRcriUpdate
from database.schemas.persons import PersonCreate, PersonRead, PersonUpdate
from database.schemas.soba import SobaRead, SobaCreate, SobaUpdate
from database.schemas.stopbang import StopBangRead, StopBangInput
from database.schemas.slice_t0 import SliceT0Input, SliceT0Read
from database.schemas.slice_t1 import SliceT1Input, SliceT1Read
from database.schemas.slice_t2 import SliceT2Input, SliceT2Read
from database.services.ariscat import AriscatService
from database.services.caprini import CapriniService
from database.services.elganzouri import ElGanzouriService
from database.services.lee import LeeRcriService
from database.services.persons import PersonsService
from database.services.soba import SobaService
from database.services.stopbang import StopBangService
from database.services.slice_t0 import SliceT0Service
from database.services.slice_t1 import SliceT1Service
from database.services.slice_t2 import SliceT2Service
from database.schemas.slice_t3 import SliceT3Input, SliceT3Read
from database.services.slice_t3 import SliceT3Service
from database.schemas.slice_t4 import SliceT4Input, SliceT4Read
from database.services.slice_t4 import SliceT4Service
from database.schemas.slice_t5 import SliceT5Input, SliceT5Read
from database.services.slice_t5 import SliceT5Service
from database.schemas.slice_t6 import SliceT6Input, SliceT6Read
from database.services.slice_t6 import SliceT6Service
from database.schemas.slice_t7 import SliceT7Input, SliceT7Read
from database.services.slice_t7 import SliceT7Service
from database.schemas.slice_t8 import SliceT8Input, SliceT8Read
from database.services.slice_t8 import SliceT8Service
from database.services.utils import NotFoundError


def create_person(
    card_number,
    anesthesia_type,
    last_name,
    first_name,
    patronymic,
    birth_date,
    inclusion_date,
    height,
    weight,
    gender,
) -> PersonRead:
    with SessionLocal() as session:
        service = PersonsService(session)
        p = service.create_person(
            PersonCreate(
                card_number=card_number,
                anesthesia_type=anesthesia_type,
                last_name=last_name,
                first_name=first_name,
                patronymic=patronymic,
                birth_date=birth_date,
                inclusion_date=inclusion_date,
                height=height,
                weight=weight,
                gender=gender,
            )
        )
        return p


def get_person(person_id):
    with SessionLocal() as session:
        service = PersonsService(session)
        p = service.get_person(person_id)
        return p


def elg_get_result(person_id: int) -> ElGanzouriRead | None:
    """Вернёт сохранённый результат или None, если нет."""
    with SessionLocal() as session:
        svc = ElGanzouriService(session)
        try:
            return svc.get_result(person_id)
        except NotFoundError:
            return None


def elg_upsert_result(person_id: int, data: ElGanzouriInput) -> ElGanzouriRead:
    """Создаёт/обновляет результат шкалы и возвращает его."""
    with SessionLocal() as session:
        svc = ElGanzouriService(session)
        saved = svc.upsert_result(person_id, data)
        return saved


def ar_get_result(person_id: int) -> AriscatRead | None:
    """Вернёт сохранённый результат ARISCAT или None, если его ещё нет."""
    with SessionLocal() as session:
        svc = AriscatService(session)
        try:
            return svc.get_result(person_id)
        except NotFoundError:
            return None


def ar_upsert_result(person_id: int, data: AriscatInput) -> AriscatRead:
    """Создаёт/обновляет результат ARISCAT и возвращает его."""
    with SessionLocal() as session:
        svc = AriscatService(session)
        saved = svc.upsert_result(person_id, data)
        return saved


def ar_clear_result(person_id: int) -> bool:
    """Удаляет результат ARISCAT и сбрасывает флаг заполнения."""
    with SessionLocal() as session:
        svc = AriscatService(session)
        return svc.clear_result(person_id)


def sb_get_result(person_id: int) -> StopBangRead | None:
    with SessionLocal() as session:
        svc = StopBangService(session)
        try:
            return svc.get_result(person_id)
        except NotFoundError:
            return None


def sb_upsert_result(person_id: int, data: StopBangInput) -> StopBangRead:
    with SessionLocal() as session:
        svc = StopBangService(session)
        return svc.upsert_result(person_id, data)


def sb_clear_result(person_id: int) -> bool:
    with SessionLocal() as session:
        svc = StopBangService(session)
        return svc.clear_result(person_id)


def get_soba(person_id: int) -> SobaRead | None:
    """Вернёт сохранённую SOBA или None, если записи ещё нет."""
    with SessionLocal() as session:
        svc = SobaService(session)
        try:
            return svc.get_for_person(person_id)
        except NotFoundError:
            return None


def upsert_soba(person_id: int, data: SobaCreate | SobaUpdate) -> SobaRead:
    with SessionLocal() as session:
        svc = SobaService(session)
        return svc.upsert_for_person(person_id, data)


def delete_soba(person_id: int) -> bool:
    with SessionLocal() as session:
        svc = SobaService(session)
        return svc.delete_for_person(person_id)


def update_person_fields(person_id: int, **fields):
    """Частичное обновление полей пациента (age/height/weight и т.п.)."""
    with SessionLocal() as session:
        svc = PersonsService(session)
        return svc.update_person(person_id, PersonUpdate(**fields))


def search_persons(query: str, limit: int = 50, offset: int = 0):
    with SessionLocal() as session:
        svc = PersonsService(session)
        return svc.search_persons(query, limit=limit, offset=offset)


def rcri_get_result(person_id: int) -> LeeRcriRead | None:
    with SessionLocal() as session:
        svc = LeeRcriService(session)
        try:
            return svc.get_result(person_id)
        except NotFoundError:
            return None


def rcri_upsert_result(person_id: int, data: LeeRcriInput | LeeRcriUpdate) -> LeeRcriRead:
    with SessionLocal() as session:
        svc = LeeRcriService(session)
        return svc.upsert_result(person_id, data)


def rcri_clear_result(person_id: int) -> bool:
    with SessionLocal() as session:
        svc = LeeRcriService(session)
        return svc.clear_result(person_id)


def caprini_get_result(person_id: int) -> CapriniRead | None:
    with SessionLocal() as session:
        svc = CapriniService(session)
        try:
            return svc.get_result(person_id)
        except NotFoundError:
            return None


def caprini_upsert_result(person_id: int, data: CapriniInput) -> CapriniRead:
    with SessionLocal() as session:
        svc = CapriniService(session)
        return svc.upsert_result(person_id, data)


def caprini_clear_result(person_id: int) -> bool:
    with SessionLocal() as session:
        svc = CapriniService(session)
        return svc.clear_result(person_id)


def t0_get_result(person_id: int) -> SliceT0Read | None:
    with SessionLocal() as session:
        svc = SliceT0Service(session)
        try:
            return svc.get(person_id)
        except NotFoundError:
            return None


def t0_upsert_result(person_id: int, data: SliceT0Input) -> SliceT0Read:
    with SessionLocal() as session:
        svc = SliceT0Service(session)
        return svc.upsert(person_id, data)


def t0_clear_result(person_id: int) -> bool:
    with SessionLocal() as session:
        svc = SliceT0Service(session)
        return svc.delete(person_id)


def t1_get_result(person_id: int) -> SliceT1Read | None:
    with SessionLocal() as session:
        svc = SliceT1Service(session)
        try:
            return svc.get(person_id)
        except NotFoundError:
            return None


def t1_upsert_result(person_id: int, data: SliceT1Input) -> SliceT1Read:
    with SessionLocal() as session:
        svc = SliceT1Service(session)
        return svc.upsert(person_id, data)


def t1_clear_result(person_id: int) -> bool:
    with SessionLocal() as session:
        svc = SliceT1Service(session)
        return svc.delete(person_id)


def t2_get_result(person_id: int) -> SliceT2Read | None:
    with SessionLocal() as session:
        svc = SliceT2Service(session)
        try:
            return svc.get(person_id)
        except NotFoundError:
            return None


def t2_upsert_result(person_id: int, data: SliceT2Input) -> SliceT2Read:
    with SessionLocal() as session:
        svc = SliceT2Service(session)
        return svc.upsert(person_id, data)


def t2_clear_result(person_id: int) -> bool:
    with SessionLocal() as session:
        svc = SliceT2Service(session)
        return svc.delete(person_id)


def t3_get_result(person_id: int) -> SliceT3Read | None:
    with SessionLocal() as session:
        svc = SliceT3Service(session)
        try:
            return svc.get(person_id)
        except NotFoundError:
            return None


def t3_upsert_result(person_id: int, data: SliceT3Input) -> SliceT3Read:
    with SessionLocal() as session:
        svc = SliceT3Service(session)
        return svc.upsert(person_id, data)


def t3_clear_result(person_id: int) -> bool:
    with SessionLocal() as session:
        svc = SliceT3Service(session)
        return svc.delete(person_id)


def t4_get_result(person_id: int) -> SliceT4Read | None:
    with SessionLocal() as session:
        svc = SliceT4Service(session)
        try:
            return svc.get(person_id)
        except NotFoundError:
            return None


def t4_upsert_result(person_id: int, data: SliceT4Input) -> SliceT4Read:
    with SessionLocal() as session:
        svc = SliceT4Service(session)
        return svc.upsert(person_id, data)


def t4_clear_result(person_id: int) -> bool:
    with SessionLocal() as session:
        svc = SliceT4Service(session)
        return svc.delete(person_id)


def t5_get_result(person_id: int) -> SliceT5Read | None:
    with SessionLocal() as session:
        svc = SliceT5Service(session)
        try:
            return svc.get(person_id)
        except NotFoundError:
            return None


def t5_upsert_result(person_id: int, data: SliceT5Input) -> SliceT5Read:
    with SessionLocal() as session:
        svc = SliceT5Service(session)
        return svc.upsert(person_id, data)


def t5_clear_result(person_id: int) -> bool:
    with SessionLocal() as session:
        svc = SliceT5Service(session)
        return svc.delete(person_id)


def t6_get_result(person_id: int) -> SliceT6Read | None:
    with SessionLocal() as session:
        svc = SliceT6Service(session)
        try:
            return svc.get(person_id)
        except NotFoundError:
            return None


def t6_upsert_result(person_id: int, data: SliceT6Input) -> SliceT6Read:
    with SessionLocal() as session:
        svc = SliceT6Service(session)
        return svc.upsert(person_id, data)


def t6_clear_result(person_id: int) -> bool:
    with SessionLocal() as session:
        svc = SliceT6Service(session)
        return svc.delete(person_id)


def t7_get_result(person_id: int) -> SliceT7Read | None:
    with SessionLocal() as session:
        svc = SliceT7Service(session)
        try:
            return svc.get(person_id)
        except NotFoundError:
            return None


def t7_upsert_result(person_id: int, data: SliceT7Input) -> SliceT7Read:
    with SessionLocal() as session:
        svc = SliceT7Service(session)
        return svc.upsert(person_id, data)


def t7_clear_result(person_id: int) -> bool:
    with SessionLocal() as session:
        svc = SliceT7Service(session)
        return svc.delete(person_id)


def t8_get_result(person_id: int) -> SliceT8Read | None:
    with SessionLocal() as session:
        svc = SliceT8Service(session)
        try:
            return svc.get(person_id)
        except NotFoundError:
            return None


def t8_upsert_result(person_id: int, data: SliceT8Input) -> SliceT8Read:
    with SessionLocal() as session:
        svc = SliceT8Service(session)
        return svc.upsert(person_id, data)


def t8_clear_result(person_id: int) -> bool:
    with SessionLocal() as session:
        svc = SliceT8Service(session)
        return svc.delete(person_id)

