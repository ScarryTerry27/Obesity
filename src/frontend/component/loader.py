import io
from importlib import import_module

import pandas as pd
import streamlit as st

import database.functions as db_funcs
from frontend.general import create_big_button
from frontend.utils import change_menu_item


# ===== helpers =====
def _safe(fetch_fn, *args, label="", default=None):
    """Безопасный вызов обёртки: ловим любые ошибки и показываем их в UI, возвращаем default."""
    try:
        return fetch_fn(*args)
    except Exception as e:
        st.warning(f"⚠️ Ошибка при получении {label or fetch_fn.__name__}: {e}")
        return default


def _bmi(weight_kg, height_cm):
    try:
        if not weight_kg or not height_cm:
            return None
        h_m = float(height_cm) / 100.0
        if h_m <= 0:
            return None
        return round(float(weight_kg) / (h_m * h_m), 1)
    except Exception:
        return None


def _elg_plan(score):
    if score is None: return "—"
    if 0 <= score <= 3: return "Обычная ларингоскопия"
    if 4 <= score <= 7: return "Видеоларингоскопия"
    return "Интубация в сознании (бронхоскопия)"


def _stopbang_label(level):
    if level is None: return "—"
    return ["Низкий", "Промежуточный", "Высокий"][max(0, min(2, int(level)))]


def _caprini_label(level):
    if level is None: return "—"
    return ["Очень низкий", "Низкий", "Умеренный", "Высокий", "Очень высокий"][max(0, min(4, int(level)))]


def _las_vegas_label(level):
    if level is None:
        return "—"
    return ["Низкий", "Промежуточный", "Высокий"][max(0, min(2, int(level)))]


def _rcri_risk(score):
    if score is None: return "—"
    if score == 0: return "≈0.4%"
    if score == 1: return "≈0.9%"
    if score == 2: return "≈7%"
    return "≈11%+"


def export_patient_data():
    person_stub = st.session_state.get("current_patient_info")
    if not person_stub:
        st.error("Пациент не выбран.")
        return

    st.title("📤 Выгрузка данных пациента")

    # 1) Берём «свежего» пациента
    person = _safe(db_funcs.get_person, person_stub.id, label="карточки пациента")
    if not person:
        st.error("Не удалось загрузить карточку пациента.")
        return

    # 2) Подтягиваем все шкалы (каждый вызов безопасный)
    from database.schemas.elganzouri import ElGanzouriRead
    from database.schemas.ariscat import AriscatRead
    from database.schemas.stopbang import StopBangRead

    elg = _safe(db_funcs.elg_get_result, person.id, label="El-Ganzouri")  # -> ElGanzouriRead | None
    ar = _safe(db_funcs.ar_get_result, person.id, label="ARISCAT")  # -> AriscatRead | None
    sb = _safe(db_funcs.sb_get_result, person.id, label="STOP-BANG")  # -> StopBangRead | None
    soba = _safe(db_funcs.get_soba, person.id, label="SOBA")  # -> SobaRead | None
    rcri = _safe(db_funcs.rcri_get_result, person.id, label="RCRI")  # -> LeeRcriRead | None
    cap = _safe(db_funcs.caprini_get_result, person.id, label="Caprini")  # -> CapriniRead | None
    lv = _safe(db_funcs.lv_get_result, person.id, label="Las Vegas")
    qor = _safe(db_funcs.qor15_get_result, person.id, label="QoR-15")
    ald = _safe(db_funcs.ald_get_result, person.id, label="Aldrete")
    mmse_t0 = _safe(db_funcs.mmse_get_result, person.id, 0, label="MMSE t0")
    mmse_t10 = _safe(db_funcs.mmse_get_result, person.id, 10, label="MMSE t10")

    # 2b) Подтягиваем все срезы динамически (T0…T12)
    slices_data = []
    for idx in range(13):
        getter = getattr(db_funcs, f"t{idx}_get_result", None)
        data = _safe(getter, person.id, label=f"срез T{idx}") if getter else None
        schema_module = import_module(f"database.schemas.slice_t{idx}")
        schema_cls = getattr(schema_module, f"SliceT{idx}Input")
        slices_data.append((f"T{idx}", data, schema_cls))

    # 3) Собираем одну строку с максимумом защит
    def g(obj, name, default=None):
        return getattr(obj, name, default) if obj is not None else default

    atype = g(person, "anesthesia_type", None)

    base_info = {
        "patient_id": person.id,
        "№ карты": g(person, "card_number", ""),
        "Фамилия": g(person, "last_name", ""),
        "Имя": g(person, "first_name", ""),
        "Отчество": g(person, "patronymic", ""),
        "Дата включения": g(person, "inclusion_date", None),
        "Тип анестезии": atype.value if atype else "",
        "Возраст (лет)": g(person, "age", None),
        "Рост (см)": g(person, "height", None),
        "Вес (кг)": g(person, "weight", None),
        "Пол": ("Ж" if bool(getattr(person, "gender", False)) else "М"),
        "ИМТ": _bmi(g(person, "weight", None), g(person, "height", None)),
    }

    row_scales = dict(base_info)
    row_slices = dict(base_info)

    def add_scale(row, prefix, obj, schema):
        fields = [
            f for f in schema.model_fields
            if f not in {"id", "scales_id", "total_score", "risk_level"}
        ]
        for field in fields:
            row[f"{prefix}: {field}"] = getattr(obj, field, None) if obj else None
        row[f"{prefix}: сумма"] = getattr(obj, "total_score", None) if obj else None

    EmptySchema = type("EmptySchema", (), {"model_fields": {}})

    # El-Ganzouri
    add_scale(row_scales, "ELG", elg, ElGanzouriRead)
    if elg is not None:
        row_scales["ELG: рекомендация"] = _elg_plan(elg.total_score)

    # ARISCAT
    add_scale(row_scales, "ARISCAT", ar, AriscatRead)

    # STOP-BANG
    add_scale(row_scales, "STOP-BANG", sb, StopBangRead)
    if sb is not None:
        row_scales["STOP-BANG: риск"] = _stopbang_label(sb.risk_level)

    # SOBA
    add_scale(row_scales, "SOBA", soba, type(soba) if soba else EmptySchema)
    if soba is not None:
        row_scales["SOBA: STOP-BANG риск (кэш)"] = _stopbang_label(
            getattr(soba, "stopbang_risk_cached", None)
        )

    # Lee RCRI
    add_scale(row_scales, "RCRI", rcri, type(rcri) if rcri else EmptySchema)
    if rcri is not None:
        row_scales["RCRI: риск (частота осложнений)"] = _rcri_risk(rcri.total_score)

    # Caprini
    add_scale(row_scales, "Caprini", cap, type(cap) if cap else EmptySchema)
    if cap is not None:
        row_scales["Caprini: риск"] = _caprini_label(cap.risk_level)

    # Las Vegas
    add_scale(row_scales, "Las Vegas", lv, type(lv) if lv else EmptySchema)
    if lv is not None:
        row_scales["Las Vegas: риск"] = _las_vegas_label(getattr(lv, "risk_level", None))

    # QoR-15
    add_scale(row_scales, "QoR-15", qor, type(qor) if qor else EmptySchema)

    # Aldrete
    add_scale(row_scales, "Aldrete", ald, type(ald) if ald else EmptySchema)

    # MMSE
    add_scale(row_scales, "MMSE t0", mmse_t0, type(mmse_t0) if mmse_t0 else EmptySchema)
    add_scale(row_scales, "MMSE t10", mmse_t10, type(mmse_t10) if mmse_t10 else EmptySchema)

    # 4) Добавляем все поля срезов
    for name, data, schema in slices_data:
        for field in schema.model_fields.keys():
            row_slices[f"{name}: {field}"] = getattr(data, field, None) if data is not None else None

    # 5) Покажем и дадим скачать
    df_scales = pd.DataFrame([row_scales])
    df_slices = pd.DataFrame([row_slices])
    df_scales.replace({True: 1, False: 0}, inplace=True)
    df_slices.replace({True: 1, False: 0}, inplace=True)
    st.markdown("### Предпросмотр шкал")
    st.dataframe(df_scales, width="stretch")
    st.markdown("### Предпросмотр срезов")
    st.dataframe(df_slices, width="stretch")

    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
        df_scales.to_excel(writer, index=False, sheet_name="Шкалы")
        df_slices.to_excel(writer, index=False, sheet_name="Срезы")

    st.download_button(
        "⬇️ Скачать Excel",
        data=excel_buf.getvalue(),
        file_name=f"patient_{person.id}_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    st.caption(
        "Если какая-то шкала или срез не заполнены, в выгрузке будут пустые значения для их полей."
    )
    create_big_button(
        "⬅️ Назад",
        on_click=change_menu_item,
        kwargs={"item": "diagnosis_patient"},
        key="back_btn",
    )
