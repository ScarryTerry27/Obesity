from sqlalchemy.orm import declarative_base, relationship

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    Enum as SAEnum,
    SmallInteger,
    Float,
    String,
    Boolean,
    Date,
)
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property

from database.enums.anesthesia import AnesthesiaType
from database.enums.ariscat import (
    AriscatAge,
    AriscatSpO2,
    AriscatRespInfect,
    AriscatAnemia,
    AriscatIncision,
    AriscatDuration,
    AriscatEmergency,
)
from database.enums.elganzouri import (
    DifficultIntubationHx,
    WeightBand,
    MandibleProtrusion,
    NeckMobility,
    Mallampati,
    Thyromental,
    MouthOpening,
)

Base = declarative_base()


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    card_number = Column(String(64), nullable=True)
    anesthesia_type = Column(SAEnum(AnesthesiaType, name="anesthesia_type"), nullable=True)
    last_name = Column(String(128), nullable=False)
    first_name = Column(String(128), nullable=False)
    patronymic = Column(String(128), nullable=True)
    birth_date = Column(Date, nullable=False)
    inclusion_date = Column(Date, nullable=False, server_default=func.current_date())
    height = Column(Integer, nullable=False)  # Рост (см)
    weight = Column(Integer, nullable=False)  # Вес (кг)
    gender = Column(Boolean, nullable=False, default=False)
    # False (0) = мужской, True (1) = женский

    scales = relationship(
        "PersonScales",
        back_populates="person",
        uselist=False,
        cascade="all, delete-orphan",
    )

    slices = relationship(
        "PersonSlices",
        back_populates="person",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @hybrid_property
    def fio(self):
        parts = [self.last_name, self.first_name, self.patronymic]
        return " ".join(p for p in parts if p)

    @hybrid_property
    def age(self):
        from datetime import date

        ref = self.inclusion_date or date.today()
        if not self.birth_date:
            return None
        return (
            ref.year
            - self.birth_date.year
            - ((ref.month, ref.day) < (self.birth_date.month, self.birth_date.day))
        )

    def __repr__(self):
        sex = "Ж" if self.gender else "М"
        return (
            f"<Person(id={self.id}, fio='{self.fio}', "
            f"age={self.age}, height={self.height}, weight={self.weight}, gender={sex})>"
        )


class PersonScales(Base):
    """
    Таблица со статусами заполнения шкал для пациента.
    По умолчанию все шкалы НЕ заполнены.
    """
    __tablename__ = "person_scales"
    __table_args__ = (
        UniqueConstraint("person_id", name="uq_person_scales_person_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True)

    # ЯВНЫЕ статусы
    el_ganzouri_filled = Column(Boolean, nullable=False, default=False)
    ariscat_filled = Column(Boolean, nullable=False, default=False)
    stopbang_filled = Column(Boolean, nullable=False, default=False)
    soba_filled = Column(Boolean, nullable=False, default=False)
    lee_rcri_filled = Column(Boolean, nullable=False, default=False)
    caprini_filled = Column(Boolean, nullable=False, default=False)

    # Технические поля
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    person = relationship("Person", back_populates="scales", uselist=False)

    # Связи 1:1 к результатам КОНКРЕТНЫХ шкал
    el_ganzouri = relationship(
        "ElGanzouriResult", back_populates="scales",
        uselist=False, cascade="all, delete-orphan"
    )
    ariscat = relationship(
        "AriscatResult", back_populates="scales",
        uselist=False, cascade="all, delete-orphan"
    )
    stopbang = relationship(  # <— только STOP-BANG
        "StopBangResult", back_populates="scales",
        uselist=False, cascade="all, delete-orphan"
    )
    soba = relationship(  # <— только SOBA
        "SobaAssessment", back_populates="scales",
        uselist=False, cascade="all, delete-orphan"
    )
    lee_rcri = relationship(
        "LeeRcriResult", back_populates="scales",
        uselist=False, cascade="all, delete-orphan"
    )
    caprini = relationship(
        "CapriniResult", back_populates="scales",
        uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<PersonScales(person_id={self.person_id}, "
            f"el_ganzouri={self.el_ganzouri_filled}, "
            f"ariscat={self.ariscat_filled}, "
            f"stopbang={self.stopbang_filled}, "
            f"soba={self.soba_filled}, "
            f"lee_rcri={self.lee_rcri_filled}, "
            f"caprini={self.caprini_filled})>"
        )


class PersonSlices(Base):
    """
    Таблица со статусами заполнения срезов для пациента.
    По умолчанию все срезы НЕ заполнены.
    """

    __tablename__ = "person_slices"
    __table_args__ = (
        UniqueConstraint("person_id", name="uq_person_slices_person_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(
        Integer, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # ЯВНЫЕ статусы
    t0_filled = Column(Boolean, nullable=False, default=False)
    t1_filled = Column(Boolean, nullable=False, default=False)
    t2_filled = Column(Boolean, nullable=False, default=False)
    t3_filled = Column(Boolean, nullable=False, default=False)
    t4_filled = Column(Boolean, nullable=False, default=False)
    t5_filled = Column(Boolean, nullable=False, default=False)
    t6_filled = Column(Boolean, nullable=False, default=False)
    t7_filled = Column(Boolean, nullable=False, default=False)
    t8_filled = Column(Boolean, nullable=False, default=False)
    t9_filled = Column(Boolean, nullable=False, default=False)
    t10_filled = Column(Boolean, nullable=False, default=False)
    t11_filled = Column(Boolean, nullable=False, default=False)
    t12_filled = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    person = relationship("Person", back_populates="slices", uselist=False)

    # Связи 1:1 к конкретным таблицам срезов
    t0 = relationship("SliceT0", back_populates="slices", uselist=False, cascade="all, delete-orphan")
    t1 = relationship("SliceT1", back_populates="slices", uselist=False, cascade="all, delete-orphan")
    t2 = relationship("SliceT2", back_populates="slices", uselist=False, cascade="all, delete-orphan")
    t3 = relationship("SliceT3", back_populates="slices", uselist=False, cascade="all, delete-orphan")
    t4 = relationship("SliceT4", back_populates="slices", uselist=False, cascade="all, delete-orphan")
    t5 = relationship("SliceT5", back_populates="slices", uselist=False, cascade="all, delete-orphan")
    t6 = relationship("SliceT6", back_populates="slices", uselist=False, cascade="all, delete-orphan")
    t7 = relationship("SliceT7", back_populates="slices", uselist=False, cascade="all, delete-orphan")
    t8 = relationship("SliceT8", back_populates="slices", uselist=False, cascade="all, delete-orphan")
    t9 = relationship("SliceT9", back_populates="slices", uselist=False, cascade="all, delete-orphan")
    t10 = relationship("SliceT10", back_populates="slices", uselist=False, cascade="all, delete-orphan")
    t11 = relationship("SliceT11", back_populates="slices", uselist=False, cascade="all, delete-orphan")
    t12 = relationship("SliceT12", back_populates="slices", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        flags = ", ".join(
            f"t{i}={getattr(self, f't{i}_filled')}" for i in range(13)
        )
        return f"<PersonSlices(person_id={self.person_id}, {flags})>"


class SliceT0(Base):
    """Placeholder table for slice T0 data."""

    __tablename__ = "slice_t0"
    __table_args__ = (UniqueConstraint("slices_id", name="uq_slice_t0_slices"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    slices_id = Column(
        Integer, ForeignKey("person_slices.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    slices = relationship("PersonSlices", back_populates="t0")


class SliceT1(Base):
    """Placeholder table for slice T1 data."""

    __tablename__ = "slice_t1"
    __table_args__ = (UniqueConstraint("slices_id", name="uq_slice_t1_slices"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    slices_id = Column(
        Integer, ForeignKey("person_slices.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    slices = relationship("PersonSlices", back_populates="t1")


class SliceT2(Base):
    """Placeholder table for slice T2 data."""

    __tablename__ = "slice_t2"
    __table_args__ = (UniqueConstraint("slices_id", name="uq_slice_t2_slices"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    slices_id = Column(
        Integer, ForeignKey("person_slices.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    slices = relationship("PersonSlices", back_populates="t2")


class SliceT3(Base):
    """Placeholder table for slice T3 data."""

    __tablename__ = "slice_t3"
    __table_args__ = (UniqueConstraint("slices_id", name="uq_slice_t3_slices"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    slices_id = Column(
        Integer, ForeignKey("person_slices.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    slices = relationship("PersonSlices", back_populates="t3")


class SliceT4(Base):
    """Placeholder table for slice T4 data."""

    __tablename__ = "slice_t4"
    __table_args__ = (UniqueConstraint("slices_id", name="uq_slice_t4_slices"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    slices_id = Column(
        Integer, ForeignKey("person_slices.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    slices = relationship("PersonSlices", back_populates="t4")


class SliceT5(Base):
    """Placeholder table for slice T5 data."""

    __tablename__ = "slice_t5"
    __table_args__ = (UniqueConstraint("slices_id", name="uq_slice_t5_slices"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    slices_id = Column(
        Integer, ForeignKey("person_slices.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    slices = relationship("PersonSlices", back_populates="t5")


class SliceT6(Base):
    """Placeholder table for slice T6 data."""

    __tablename__ = "slice_t6"
    __table_args__ = (UniqueConstraint("slices_id", name="uq_slice_t6_slices"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    slices_id = Column(
        Integer, ForeignKey("person_slices.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    slices = relationship("PersonSlices", back_populates="t6")


class SliceT7(Base):
    """Placeholder table for slice T7 data."""

    __tablename__ = "slice_t7"
    __table_args__ = (UniqueConstraint("slices_id", name="uq_slice_t7_slices"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    slices_id = Column(
        Integer, ForeignKey("person_slices.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    slices = relationship("PersonSlices", back_populates="t7")


class SliceT8(Base):
    """Placeholder table for slice T8 data."""

    __tablename__ = "slice_t8"
    __table_args__ = (UniqueConstraint("slices_id", name="uq_slice_t8_slices"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    slices_id = Column(
        Integer, ForeignKey("person_slices.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    slices = relationship("PersonSlices", back_populates="t8")


class SliceT9(Base):
    """Placeholder table for slice T9 data."""

    __tablename__ = "slice_t9"
    __table_args__ = (UniqueConstraint("slices_id", name="uq_slice_t9_slices"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    slices_id = Column(
        Integer, ForeignKey("person_slices.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    slices = relationship("PersonSlices", back_populates="t9")


class SliceT10(Base):
    """Placeholder table for slice T10 data."""

    __tablename__ = "slice_t10"
    __table_args__ = (UniqueConstraint("slices_id", name="uq_slice_t10_slices"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    slices_id = Column(
        Integer, ForeignKey("person_slices.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    slices = relationship("PersonSlices", back_populates="t10")


class SliceT11(Base):
    """Placeholder table for slice T11 data."""

    __tablename__ = "slice_t11"
    __table_args__ = (UniqueConstraint("slices_id", name="uq_slice_t11_slices"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    slices_id = Column(
        Integer, ForeignKey("person_slices.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    slices = relationship("PersonSlices", back_populates="t11")


class SliceT12(Base):
    """Placeholder table for slice T12 data."""

    __tablename__ = "slice_t12"
    __table_args__ = (UniqueConstraint("slices_id", name="uq_slice_t12_slices"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    slices_id = Column(
        Integer, ForeignKey("person_slices.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    slices = relationship("PersonSlices", back_populates="t12")


class ElGanzouriResult(Base):
    __tablename__ = "el_ganzouri_results"
    __table_args__ = (UniqueConstraint("scales_id", name="uq_elganzouri_scales"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    scales_id = Column(Integer, ForeignKey("person_scales.id", ondelete="CASCADE"),
                       nullable=False, index=True)

    # --- Храним выбранные категории (каждая уже кодируется в 0/1/2 по шкале) ---
    mouth_opening = Column(SAEnum(MouthOpening), nullable=False)
    thyromental = Column(SAEnum(Thyromental), nullable=False)
    mallampati = Column(SAEnum(Mallampati), nullable=False)
    neck_mobility = Column(SAEnum(NeckMobility), nullable=False)
    mandible_protrusion = Column(SAEnum(MandibleProtrusion), nullable=False)
    weight_band = Column(SAEnum(WeightBand), nullable=False)
    diff_intubation_hx = Column(SAEnum(DifficultIntubationHx), nullable=False)

    # --- (необязательно) исходные измерения/наблюдения, если хочешь хранить «сырые» данные ---
    interincisor_cm = Column(Float)  # фактическое расстояние между резцами
    thyromental_cm = Column(Float)  # фактическое ТМР
    neck_ext_deg = Column(Float)  # фактическая экстензия шеи (°)
    weight_kg = Column(Float)  # фактическая масса тела
    mallampati_raw = Column(SmallInteger)  # если где-то фиксируешь I–IV как 1–4

    # --- служебные поля ---
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    scales = relationship("PersonScales", back_populates="el_ganzouri")

    # --- сумма баллов как гибридное свойство ---
    @hybrid_property
    def total_score(self) -> int:
        return (
                self.mouth_opening.value +
                self.thyromental.value +
                self.mallampati.value +
                self.neck_mobility.value +
                self.mandible_protrusion.value +
                self.weight_band.value +
                self.diff_intubation_hx.value
        )

    def __repr__(self):
        return f"<ElGanzouriResult(scales_id={self.scales_id}, total={self.total_score})>"


class AriscatResult(Base):
    """
    Результат шкалы ARISCAT (один-на-один с PersonScales).
    Хранит и «сырые» значения (age, spo2 и т.д.), и их категорию (enum),
    и суммарный балл total_score.
    """
    __tablename__ = "ariscat_results"
    __table_args__ = (UniqueConstraint("scales_id", name="uq_ariscat_scales"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    scales_id = Column(Integer, ForeignKey("person_scales.id", ondelete="CASCADE"),
                       nullable=False, index=True)

    # --- сырые значения для удобства UI/аналитики ---
    age_years = Column(Integer, nullable=True)  # возраст, лет
    spo2_percent = Column(Integer, nullable=True)  # SpO2, %
    had_resp_infection_last_month = Column(Boolean, nullable=True)
    has_anemia_hb_le_100 = Column(Boolean, nullable=True)
    incision_raw = Column(String(32), nullable=True)  # peripheral / upper_abd / intrathoracic (опц.)
    duration_minutes = Column(Integer, nullable=True)  # длительность опер., мин
    is_emergency = Column(Boolean, nullable=True)

    # --- категории по шкале ---
    cat_age = Column(SAEnum(AriscatAge), nullable=False)
    cat_spo2 = Column(SAEnum(AriscatSpO2), nullable=False)
    cat_resp_inf = Column(SAEnum(AriscatRespInfect), nullable=False)
    cat_anemia = Column(SAEnum(AriscatAnemia), nullable=False)
    cat_incision = Column(SAEnum(AriscatIncision), nullable=False)
    cat_duration = Column(SAEnum(AriscatDuration), nullable=False)
    cat_emerg = Column(SAEnum(AriscatEmergency), nullable=False)

    total_score = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # связь назад к PersonScales
    scales = relationship("PersonScales", back_populates="ariscat")


class StopBangResult(Base):
    """
    Результат STOP-BANG (один-на-один с PersonScales).
    S,T,O,P,B,A,N,G — булевые признаки.
    Храним и фактические численные значения (BMI, шея, возраст) для UI / аудита.
    """
    __tablename__ = "stopbang_results"
    __table_args__ = (UniqueConstraint("scales_id", name="uq_stopbang_scales"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    scales_id = Column(Integer, ForeignKey("person_scales.id", ondelete="CASCADE"),
                       nullable=False, index=True)

    # пункты STOP-BANG
    s_snoring = Column(Boolean, nullable=False, default=False)
    t_tired_daytime = Column(Boolean, nullable=False, default=False)
    o_observed_apnea = Column(Boolean, nullable=False, default=False)
    p_hypertension = Column(Boolean, nullable=False, default=False)
    b_bmi_ge_35 = Column(Boolean, nullable=False, default=False)
    a_age_gt_50 = Column(Boolean, nullable=False, default=False)
    n_neck_gt_40 = Column(Boolean, nullable=False, default=False)
    g_male = Column(Boolean, nullable=False, default=False)

    # фактические значения (не обязательны, но полезны)
    bmi_value = Column(Float, nullable=True)
    age_years = Column(Integer, nullable=True)
    neck_circ_cm = Column(Float, nullable=True)

    total_score = Column(Integer, nullable=False, default=0)  # 0–8
    risk_level = Column(Integer, nullable=False, default=0)  # 0=низкий, 1=умеренный, 2=высокий

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    scales = relationship("PersonScales", back_populates="stopbang")


class SobaAssessment(Base):
    """
    Рекомендации SOBA (Society for Obesity and Bariatric Anaesthesia)
    — агрегирует дооперационные решения / маркеры риска для пациентов с ожирением.
    НЕ балльная шкала, хранит флаги и рекомендации.
    """
    __tablename__ = "soba_assessments"
    __table_args__ = (
        UniqueConstraint("scales_id", name="uq_soba_scales"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # связь 1:1 c агрегатором шкал конкретного пациента
    scales_id = Column(Integer, ForeignKey("person_scales.id", ondelete="CASCADE"),
                       nullable=False, index=True)

    # --- Ключевые маркеры / «red flags» из гайдлайна SOBA ---
    poor_functional_status = Column(Boolean, nullable=False, default=False)  # Плохие функциональные данные
    ekg_changes = Column(Boolean, nullable=False, default=False)  # Изменения ЭКГ
    uncontrolled_htn_ihd = Column(Boolean, nullable=False, default=False)  # Неконтр. АГ или ИБС
    spo2_room_air_lt_94 = Column(Boolean, nullable=False, default=False)  # SpO2 < 94% на воздухе
    hypercapnia_co2_gt_28 = Column(Boolean, nullable=False, default=False)  # PaCO2 > 28 мм рт.ст.
    vte_history = Column(Boolean, nullable=False, default=False)  # ТГВ/ТЭЛА в анамнезе

    # --- Зависимости от STOP-BANG (кэшируем, чтобы видеть контекст) ---
    stopbang_score_cached = Column(Integer, nullable=True)  # 0–8, если посчитан
    stopbang_risk_cached = Column(Integer, nullable=True)  # 0-низкий, 1-промежуточный, 2-высокий

    # Техполя
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # backref к агрегатору
    scales = relationship("PersonScales", back_populates="soba")

    def __repr__(self) -> str:
        return (
            f"<SobaAssessment(scales_id={self.scales_id}, "
            f"stopbang_score={self.stopbang_score_cached}, "
            f"red_flags=["
            f"poor_fx={self.poor_functional_status}, "
            f"ekg={self.ekg_changes}, "
            f"htn_ihd={self.uncontrolled_htn_ihd}, "
            f"spo2_lt_94={self.spo2_room_air_lt_94}, "
            f"co2_gt_28={self.hypercapnia_co2_gt_28}, "
            f"vte_hist={self.vte_history}"
            f"])>"
        )


class LeeRcriResult(Base):
    """
    Пересмотренный индекс кардиального риска (RCRI, индекс Lee).
    1:1 с PersonScales.
    """
    __tablename__ = "lee_rcri_results"
    __table_args__ = (UniqueConstraint("scales_id", name="uq_lee_rcri_scales"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    scales_id = Column(Integer, ForeignKey("person_scales.id", ondelete="CASCADE"),
                       nullable=False, index=True)

    # 6 предикторов (бинарные)
    high_risk_surgery = Column(Boolean, nullable=False, default=False)  # операция высокого риска
    ischemic_heart_disease = Column(Boolean, nullable=False, default=False)  # ИБС
    congestive_heart_failure = Column(Boolean, nullable=False, default=False)  # ХСН
    cerebrovascular_disease = Column(Boolean, nullable=False, default=False)  # ОНМК/ТИА в анамнезе
    diabetes_on_insulin = Column(Boolean, nullable=False, default=False)  # СД на инсулине
    creatinine_gt_180_umol_l = Column(Boolean, nullable=False, default=False)  # креатинин > 180 мкмоль/л

    # итог
    total_score = Column(Integer, nullable=False, default=0)  # 0..6
    risk_percent = Column(Float, nullable=False, default=0.4)  # 0.4 / 0.9 / 7 / 11

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    scales = relationship("PersonScales", back_populates="lee_rcri")


class CapriniResult(Base):
    __tablename__ = "caprini_results"
    __table_args__ = (UniqueConstraint("scales_id", name="uq_caprini_scales"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    scales_id = Column(Integer, ForeignKey("person_scales.id", ondelete="CASCADE"), nullable=False, index=True)

    # --- Сырые численные для авто-расчёта (опционально) ---
    age_years = Column(Integer, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    bmi_value = Column(Float, nullable=True)  # кэш ИМТ (если считаем)

    # --- Категории возраста (храним как bool для прозрачности) ---
    age_41_60 = Column(Boolean, nullable=False, default=False)  # +1
    age_61_74 = Column(Boolean, nullable=False, default=False)  # +2
    age_ge_75 = Column(Boolean, nullable=False, default=False)  # +3

    # --- ИМТ ---
    bmi_gt_25 = Column(Boolean, nullable=False, default=False)  # +1

    # --- 1 балл ---
    leg_swelling_now = Column(Boolean, nullable=False, default=False)  # отёки нижних конечностей
    varicose_veins = Column(Boolean, nullable=False, default=False)
    sepsis_lt_1m = Column(Boolean, nullable=False, default=False)
    severe_lung_disease_lt_1m = Column(Boolean, nullable=False, default=False)  # пневмония < 1 мес и т.п.
    ocp_or_hrt = Column(Boolean, nullable=False, default=False)  # ОК/ГЗТ
    pregnant_or_postpartum_lt_1m = Column(Boolean, nullable=False, default=False)
    adverse_pregnancy_history = Column(Boolean, nullable=False, default=False)  # мертворождения/повт. выкидыши и т.п.
    acute_mi = Column(Boolean, nullable=False, default=False)
    chf_now_or_lt_1m = Column(Boolean, nullable=False, default=False)
    bed_rest = Column(Boolean, nullable=False, default=False)
    ibd_history = Column(Boolean, nullable=False, default=False)  # воспалит. заб-е толстой кишки
    copd = Column(Boolean, nullable=False, default=False)  # ХОБЛ
    minor_surgery = Column(Boolean, nullable=False, default=False)
    additional_risk_factor = Column(Boolean, nullable=False, default=False)  # «какой-либо доп. фактор» (+1)

    # --- 2 балла ---
    bed_rest_gt_72h = Column(Boolean, nullable=False, default=False)
    major_surgery_lt_1m = Column(Boolean, nullable=False, default=False)  # большая хирургия < 1 мес
    cancer_current_or_past = Column(Boolean, nullable=False, default=False)
    limb_immobilization_lt_1m = Column(Boolean, nullable=False, default=False)
    central_venous_catheter = Column(Boolean, nullable=False, default=False)
    arthroscopic_surgery = Column(Boolean, nullable=False, default=False)
    laparoscopy_gt_60m = Column(Boolean, nullable=False, default=False)
    major_surgery_gt_45m = Column(Boolean, nullable=False, default=False)

    # --- 3 балла ---
    personal_vte_history = Column(Boolean, nullable=False, default=False)  # личный анамнез ВТЭО
    factor_v_leiden = Column(Boolean, nullable=False, default=False)
    prothrombin_20210a = Column(Boolean, nullable=False, default=False)
    lupus_anticoagulant = Column(Boolean, nullable=False, default=False)
    family_vte_history = Column(Boolean, nullable=False, default=False)
    hyperhomocysteinemia = Column(Boolean, nullable=False, default=False)
    hit = Column(Boolean, nullable=False, default=False)  # ГИТ
    anticardiolipin_antibodies = Column(Boolean, nullable=False, default=False)
    other_thrombophilia = Column(Boolean, nullable=False, default=False)

    # --- 5 баллов ---
    stroke_lt_1m = Column(Boolean, nullable=False, default=False)
    spinal_cord_injury_paralysis_lt_1m = Column(Boolean, nullable=False, default=False)
    multiple_trauma_lt_1m = Column(Boolean, nullable=False, default=False)
    major_joint_replacement = Column(Boolean, nullable=False, default=False)
    fracture_pelvis_or_limb = Column(Boolean, nullable=False, default=False)

    total_score = Column(Integer, nullable=False, default=0)
    risk_level = Column(Integer, nullable=False, default=0)  # 0=оч. низкий, 1=низкий, 2=умеренный, 3=высокий

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    scales = relationship("PersonScales", back_populates="caprini")
