import io
import os
from importlib import import_module

import pandas as pd
import streamlit as st

from backend.reporting import generate_patient_report

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

    # 4) Добавляем все поля срезов в основную строку
    for name, data, schema in slices_data:
        for field in schema.model_fields.keys():
            row[f"{name}: {field}"] = getattr(data, field, None) if data is not None else None

    # 5) Покажем и дадим скачать
    df = pd.DataFrame([row])
    df.replace({True: 1, False: 0}, inplace=True)
    st.markdown("### Предпросмотр")
    st.dataframe(df, width="stretch")

    excel_buf = io.BytesIO()
    df.to_excel(excel_buf, index=False)

    st.download_button(
        "⬇️ Скачать Excel",
        data=excel_buf.getvalue(),
        file_name=f"patient_{person.id}_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )

    if st.button("📄 Сформировать PDF-отчёт", key="gen_pdf_btn"):
        patient_info = {
            "id": person.id,
            "fio": person.fio,
            "age": getattr(person, "age", None),
            "height": getattr(person, "height", None),
            "weight": getattr(person, "weight", None),
        }
        scales = {
            "EL-Ganzouri": getattr(elg, "total_score", None),
            "ARISCAT": getattr(ar, "total_score", None),
            "STOP-BANG": getattr(sb, "total_score", None),
            "SOBA": getattr(soba, "total_score", None),
            "RCRI": getattr(rcri, "total_score", None),
            "Caprini": getattr(cap, "total_score", None),
        }
        pdf_path = generate_patient_report(patient_info, scales)
        st.session_state["pdf_report_path"] = pdf_path
        st.success("Отчёт сформирован")

    pdf_path = st.session_state.get("pdf_report_path")
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                "⬇️ Скачать PDF",
                data=pdf_file.read(),
                file_name=os.path.basename(pdf_path),
                mime="application/pdf",
                key="download_pdf_btn",
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
