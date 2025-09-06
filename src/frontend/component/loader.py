import json
import io
import pandas as pd
import streamlit as st

from database.functions import (
    get_person,
    elg_get_result,
    ar_get_result,
    sb_get_result,
    get_soba,
    rcri_get_result,
    caprini_get_result,
)


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
    return ["Очень низкий", "Низкий", "Умеренный", "Высокий"][max(0, min(3, int(level)))]


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
    person = _safe(get_person, person_stub.id, label="карточки пациента")
    if not person:
        st.error("Не удалось загрузить карточку пациента.")
        return

    # 2) Подтягиваем все шкалы (каждый вызов безопасный)
    elg = _safe(elg_get_result, person.id, label="El-Ganzouri")  # -> ElGanzouriRead | None
    ar = _safe(ar_get_result, person.id, label="ARISCAT")  # -> AriscatRead | None
    sb = _safe(sb_get_result, person.id, label="STOP-BANG")  # -> StopBangRead | None
    soba = _safe(get_soba, person.id, label="SOBA")  # -> SobaRead | None
    rcri = _safe(rcri_get_result, person.id, label="RCRI")  # -> LeeRcriRead | None
    cap = _safe(caprini_get_result, person.id, label="Caprini")  # -> CapriniRead | None

    # 3) Собираем одну строку с максимумом защит
    def g(obj, name, default=None):
        return getattr(obj, name, default) if obj is not None else default

    row = {
        "patient_id": person.id,
        "ФИО": g(person, "fio", ""),
        "Возраст (лет)": g(person, "age", None),
        "Рост (см)": g(person, "height", None),
        "Вес (кг)": g(person, "weight", None),
        "Пол": ("Ж" if bool(getattr(person, "gender", False)) else "М"),
        "ИМТ": _bmi(g(person, "weight", None), g(person, "height", None)),

        # El-Ganzouri
        "ELG: сумма": g(elg, "total_score", None),
        "ELG: рекомендация": _elg_plan(g(elg, "total_score", None)),

        # ARISCAT
        "ARISCAT: сумма": g(ar, "total_score", None),

        # STOP-BANG
        "STOP-BANG: сумма": g(sb, "total_score", None),
        "STOP-BANG: риск": _stopbang_label(g(sb, "risk_level", None)),

        # SOBA
        "SOBA: STOP-BANG сумма (кэш)": g(soba, "stopbang_score_cached", None),
        "SOBA: STOP-BANG риск (кэш)": _stopbang_label(g(soba, "stopbang_risk_cached", None)),
        "SOBA: плохая ФН": g(soba, "poor_functional_status", None),
        "SOBA: изменения ЭКГ": g(soba, "ekg_changes", None),
        "SOBA: неконтр. АГ/ИБС": g(soba, "uncontrolled_htn_ihd", None),
        "SOBA: SpO₂<94%": g(soba, "spo2_room_air_lt_94", None),
        "SOBA: PaCO₂>28": g(soba, "hypercapnia_co2_gt_28", None),
        "SOBA: ТГВ/ТЭЛА анамнез": g(soba, "vte_history", None),

        # Lee RCRI
        "RCRI: сумма": g(rcri, "total_score", None),
        "RCRI: риск (частота осложнений)": _rcri_risk(g(rcri, "total_score", None)),

        # Caprini
        "Caprini: сумма": g(cap, "total_score", None),
        "Caprini: риск": _caprini_label(g(cap, "risk_level", None)),
    }

    # 4) Покажем и дадим скачать
    df = pd.DataFrame([row])
    st.markdown("### Предпросмотр")
    st.dataframe(df, use_container_width=True)

    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False)
    st.download_button(
        "⬇️ Скачать CSV",
        data=csv_buf.getvalue().encode("utf-8-sig"),
        file_name=f"patient_{person.id}_export.csv",
        mime="text/csv",
        use_container_width=True,
    )

    json_str = json.dumps(row, ensure_ascii=False, indent=2)
    st.download_button(
        "⬇️ Скачать JSON",
        data=json_str.encode("utf-8"),
        file_name=f"patient_{person.id}_export.json",
        mime="application/json",
        use_container_width=True,
    )

    st.caption("Если какая-то шкала не заполнена, в выгрузке будут пустые значения для её полей.")
