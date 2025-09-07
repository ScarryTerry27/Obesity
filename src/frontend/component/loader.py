import io
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
    elg = _safe(db_funcs.elg_get_result, person.id, label="El-Ganzouri")  # -> ElGanzouriRead | None
    ar = _safe(db_funcs.ar_get_result, person.id, label="ARISCAT")  # -> AriscatRead | None
    sb = _safe(db_funcs.sb_get_result, person.id, label="STOP-BANG")  # -> StopBangRead | None
    soba = _safe(db_funcs.get_soba, person.id, label="SOBA")  # -> SobaRead | None
    rcri = _safe(db_funcs.rcri_get_result, person.id, label="RCRI")  # -> LeeRcriRead | None
    cap = _safe(db_funcs.caprini_get_result, person.id, label="Caprini")  # -> CapriniRead | None

    # 2b) Подтягиваем все срезы
    t0 = _safe(db_funcs.t0_get_result, person.id, label="срез T0")
    t1 = _safe(db_funcs.t1_get_result, person.id, label="срез T1")
    t2 = _safe(db_funcs.t2_get_result, person.id, label="срез T2")
    t3 = _safe(db_funcs.t3_get_result, person.id, label="срез T3")
    t4 = _safe(db_funcs.t4_get_result, person.id, label="срез T4")
    t5 = _safe(db_funcs.t5_get_result, person.id, label="срез T5")
    t6 = _safe(db_funcs.t6_get_result, person.id, label="срез T6")
    t7 = _safe(db_funcs.t7_get_result, person.id, label="срез T7")
    t8 = _safe(db_funcs.t8_get_result, person.id, label="срез T8")
    t9 = _safe(db_funcs.t9_get_result, person.id, label="срез T9")
    t10 = _safe(db_funcs.t10_get_result, person.id, label="срез T10")
    t11 = _safe(db_funcs.t11_get_result, person.id, label="срез T11")
    t12 = _safe(db_funcs.t12_get_result, person.id, label="срез T12")

    # 3) Собираем одну строку с максимумом защит
    def g(obj, name, default=None):
        return getattr(obj, name, default) if obj is not None else default

    atype = g(person, "anesthesia_type", None)

    row = {
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

    def add_scale(prefix, obj):
        if obj is None:
            return
        data = obj.model_dump()
        data.pop("id", None)
        data.pop("scales_id", None)
        score = data.pop("total_score", None)
        if score is not None:
            row[f"{prefix}: сумма"] = score
        for field, value in data.items():
            row[f"{prefix}: {field}"] = value

    # El-Ganzouri
    add_scale("ELG", elg)
    if elg is not None:
        row["ELG: рекомендация"] = _elg_plan(elg.total_score)

    # ARISCAT
    add_scale("ARISCAT", ar)

    # STOP-BANG
    add_scale("STOP-BANG", sb)
    if sb is not None:
        row["STOP-BANG: риск"] = _stopbang_label(sb.risk_level)

    # SOBA
    add_scale("SOBA", soba)
    if soba is not None:
        row["SOBA: STOP-BANG риск (кэш)"] = _stopbang_label(
            getattr(soba, "stopbang_risk_cached", None)
        )

    # Lee RCRI
    add_scale("RCRI", rcri)
    if rcri is not None:
        row["RCRI: риск (частота осложнений)"] = _rcri_risk(rcri.total_score)

    # Caprini
    add_scale("Caprini", cap)
    if cap is not None:
        row["Caprini: риск"] = _caprini_label(cap.risk_level)

    # 4) Составляем данные по срезам: перечисляем все поля каждой схемы,
    # даже если срез не заполнен
    from database.schemas.slice_t0 import SliceT0Input
    from database.schemas.slice_t1 import SliceT1Input
    from database.schemas.slice_t2 import SliceT2Input
    from database.schemas.slice_t3 import SliceT3Input
    from database.schemas.slice_t4 import SliceT4Input
    from database.schemas.slice_t5 import SliceT5Input
    from database.schemas.slice_t6 import SliceT6Input
    from database.schemas.slice_t7 import SliceT7Input
    from database.schemas.slice_t8 import SliceT8Input
    from database.schemas.slice_t9 import SliceT9Input
    from database.schemas.slice_t10 import SliceT10Input
    from database.schemas.slice_t11 import SliceT11Input
    from database.schemas.slice_t12 import SliceT12Input

    slice_defs = [
        ("T0", t0, SliceT0Input),
        ("T1", t1, SliceT1Input),
        ("T2", t2, SliceT2Input),
        ("T3", t3, SliceT3Input),
        ("T4", t4, SliceT4Input),
        ("T5", t5, SliceT5Input),
        ("T6", t6, SliceT6Input),
        ("T7", t7, SliceT7Input),
        ("T8", t8, SliceT8Input),
        ("T9", t9, SliceT9Input),
        ("T10", t10, SliceT10Input),
        ("T11", t11, SliceT11Input),
        ("T12", t12, SliceT12Input),
    ]

    slice_rows = []
    for name, data, schema in slice_defs:
        row_slice = {"Срез": name}
        for field in schema.model_fields.keys():
            row_slice[field] = getattr(data, field, None) if data is not None else None
        slice_rows.append(row_slice)

    # 5) Покажем и дадим скачать
    df_scales = pd.DataFrame([row])
    df_slices = pd.DataFrame(slice_rows)
    df_scales.replace({True: 1, False: 0}, inplace=True)
    df_slices.replace({True: 1, False: 0}, inplace=True)
    st.markdown("### Предпросмотр шкал")
    st.dataframe(df_scales, width="stretch")
    st.markdown("### Предпросмотр срезов")
    st.dataframe(df_slices, width="stretch")

    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf) as writer:
        df_scales.to_excel(writer, index=False, sheet_name="Шкалы")
        df_slices.to_excel(writer, index=False, sheet_name="Срезы")

    st.download_button(
        "⬇️ Скачать Excel",
        data=excel_buf.getvalue(),
        file_name=f"patient_{person.id}_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
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
