import streamlit as st

from database.functions import sb_get_result, sb_upsert_result, get_person
from database.schemas.stopbang import StopBangInput
from frontend.components import create_big_button
from frontend.utils import change_menu_item


def _sb_risk_label(level: int | None) -> str:
    if level is None:
        return ""
    return ["низкий", "промежуточный", "высокий"][max(0, min(2, int(level)))]


def _auto_defaults_from_person(person) -> tuple[int, float, float]:
    """Берём возраст, считаем BMI из веса/роста, окружность шеи оставляем пустой."""
    # ожидаем, что person.weight (кг), person.height (см), person.age (лет)
    try:
        age = int(person.age or 50)
    except Exception:
        age = 50
    try:
        w = float(person.weight or 100.0)
        h_cm = float(person.height or 170.0)
        h_m = max(h_cm / 100.0, 0.5)
        bmi = round(w / (h_m * h_m), 1)
    except Exception:
        bmi = 35.0
    # окружность шеи — не угадаем; пусть 40.0 как стартовая точка
    neck = 40.0
    return age, bmi, neck


def show_stopbang_scale():
    """Экран ввода STOP-BANG. Использует сервисный слой, без прямой работы с сессией."""
    person = st.session_state.get("current_patient_info")
    if not person:
        st.error("Пациент не выбран.")
        return

    st.subheader("Шкала STOP-BANG — скрининг СОАС")

    # 1) Подтянуть сохранённый результат, если есть
    stored = sb_get_result(person.id)

    # 2) Дефолты (если записи нет) — из карточки пациента
    age_default, bmi_default, neck_default = _auto_defaults_from_person(person)

    # Собираем значения для формы: если сохранено — берём сохранённые; иначе дефолты
    s_snoring = bool(getattr(stored, "s_snoring", False))
    t_tired = bool(getattr(stored, "t_tired_daytime", False))
    o_observed = bool(getattr(stored, "o_observed_apnea", False))
    p_htn = bool(getattr(stored, "p_hypertension", False))
    g_male = bool(getattr(stored, "g_male", (str(getattr(person, "gender", "")).lower() == "m")))
    age_years = int(getattr(stored, "age_years", age_default))
    bmi_value = float(getattr(stored, "bmi_value", bmi_default))
    neck_circ_cm = float(getattr(stored, "neck_circ_cm", neck_default))

    # Если запись есть — покажем текущий итог
    if stored:
        st.info(f"Текущие данные: баллы **{stored.total_score}** · риск **{_sb_risk_label(stored.risk_level)}**")

    with st.form("stopbang_form"):
        c1, c2 = st.columns(2)

        with c1:
            s_snoring = st.checkbox("Громкий храп (S — Snoring)", value=s_snoring)
            t_tired = st.checkbox("Дневная сонливость/усталость (T — Tired)", value=t_tired)
            o_observed = st.checkbox("Наблюдались остановки дыхания во сне (O — Observed)", value=o_observed)
            p_htn = st.checkbox("Артериальная гипертензия (P — Pressure)", value=p_htn)

        with c2:
            g_male = st.checkbox("Мужской пол (G — Gender)", value=g_male)
            age_years = st.number_input("Возраст (лет)", min_value=0, max_value=130, value=age_years, step=1)
            bmi_value = st.number_input("Индекс массы тела (кг/м²)", min_value=5.0, max_value=120.0, value=bmi_value,
                                        step=0.1)
            neck_circ_cm = st.number_input("Окружность шеи (см)", min_value=10.0, max_value=80.0, value=neck_circ_cm,
                                           step=0.5)

        submitted = st.form_submit_button("💾 Сохранить", use_container_width=True)

    if submitted:
        data = StopBangInput(
            s_snoring=s_snoring,
            t_tired_daytime=t_tired,
            o_observed_apnea=o_observed,
            p_hypertension=p_htn,
            g_male=g_male,
            age_years=age_years,
            bmi_value=bmi_value,
            neck_circ_cm=neck_circ_cm,
        )
        saved = sb_upsert_result(person.id, data)
        st.success(f"Сохранено. Баллы: **{saved.total_score}** · риск: **{_sb_risk_label(saved.risk_level)}**")
        st.session_state["current_patient_info"] = get_person(person.id)
    create_big_button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "preoperative_exam"}, key="back_btn")
