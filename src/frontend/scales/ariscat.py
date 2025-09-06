import streamlit as st

from database.functions import ar_get_result, ar_upsert_result, get_person
from database.schemas.ariscat import AriscatInput
from frontend.components import create_big_button
from frontend.utils import change_menu_item


def _risk_label(score: int) -> str:
    # типичные пороги ARISCAT: <26 низкий, 26–44 умеренный, ≥45 высокий
    if score >= 45:
        return "Высокий риск (≥45)"
    if score >= 26:
        return "Умеренный риск (26–44)"
    return "Низкий риск (<26)"


def show_ariscat_scale():
    st.subheader("Шкала ARISCAT — риск послеоперационных лёгочных осложнений")

    person = st.session_state.get("current_patient_info")  # это PersonRead
    if not person:
        st.error("Пациент не выбран.")
        return

    # 1) Тянем сохранённые значения (если есть)
    saved = ar_get_result(person.id)

    # 2) Дефолты (если нет сохранённых)
    defaults = {
        "age_years": int(getattr(person, "age", 50) or 50),
        "spo2_percent": 98,
        "had_resp_infection_last_month": False,
        "has_anemia_hb_le_100": False,
        "incision": "peripheral",  # peripheral | upper_abd | intrathoracic
        "duration_minutes": 90,  # <2ч
        "is_emergency": False,
    }

    if saved:
        defaults.update({
            "age_years": saved.age_years or defaults["age_years"],
            "spo2_percent": saved.spo2_percent or defaults["spo2_percent"],
            "had_resp_infection_last_month": (
                saved.had_resp_infection_last_month
                if saved.had_resp_infection_last_month is not None
                else defaults["had_resp_infection_last_month"]
            ),
            "has_anemia_hb_le_100": (
                saved.has_anemia_hb_le_100
                if saved.has_anemia_hb_le_100 is not None
                else defaults["has_anemia_hb_le_100"]
            ),
            "incision": saved.incision_raw or defaults["incision"],
            "duration_minutes": saved.duration_minutes or defaults["duration_minutes"],
            "is_emergency": (
                saved.is_emergency
                if saved.is_emergency is not None
                else defaults["is_emergency"]
            ),
        })
        st.info(f"Текущая сумма баллов: **{saved.total_score}** · {_risk_label(saved.total_score)}")

    # 3) UI формы
    with st.form("ariscat_form"):
        c1, c2 = st.columns(2)
        with c1:
            age_years = st.number_input(
                "Возраст (лет)", min_value=0, max_value=130, step=1, value=int(defaults["age_years"]),
                key="ar_age"
            )
            spo2_percent = st.number_input(
                "Дооперационная SpO₂ (%)", min_value=50, max_value=100, step=1, value=int(defaults["spo2_percent"]),
                key="ar_spo2"
            )
            had_inf = st.checkbox(
                "Респираторная инфекция за последний месяц", value=bool(defaults["had_resp_infection_last_month"]),
                key="ar_inf"
            )
            anemia = st.checkbox(
                "Дооперационная анемия (Hb ≤ 100 г/л)", value=bool(defaults["has_anemia_hb_le_100"]),
                key="ar_anemia"
            )
        with c2:
            incision_label = st.selectbox(
                "Хирургический разрез",
                ["Периферический", "Верхний абдоминальный", "Внутригрудной"],
                index={"peripheral": 0, "upper_abd": 1, "intrathoracic": 2}[defaults["incision"]],
                key="ar_incision"
            )
            incision_map = {
                "Периферический": "peripheral",
                "Верхний абдоминальный": "upper_abd",
                "Внутригрудной": "intrathoracic",
            }
            incision_code = incision_map[incision_label]

            dur_choice = st.selectbox(
                "Продолжительность операции",
                ["< 2 часа", "2–3 часа", "> 3 часов"],
                index=(0 if defaults["duration_minutes"] < 120 else (1 if defaults["duration_minutes"] <= 180 else 2)),
                key="ar_dur_choice",
            )
            # сохраним как минуты для бэкенда
            duration_minutes = (
                90 if dur_choice == "< 2 часа"
                else (150 if dur_choice == "2–3 часа" else 200)
            )

            emergency = st.checkbox("Экстренная операция", value=bool(defaults["is_emergency"]), key="ar_emerg")

        submitted = st.form_submit_button("💾 Сохранить", use_container_width=True)

    # 4) Сохранение
    if submitted:
        data = AriscatInput(
            age_years=age_years,
            spo2_percent=spo2_percent,
            had_resp_infection_last_month=had_inf,
            has_anemia_hb_le_100=anemia,
            incision=incision_code,
            duration_minutes=duration_minutes,
            is_emergency=emergency,
        )
        saved = ar_upsert_result(person.id, data)
        st.session_state["current_patient_info"] = get_person(person.id)
        st.success(f"Сохранено. Сумма баллов: **{saved.total_score}** · {_risk_label(saved.total_score)}")

    create_big_button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "preoperative_exam"}, key="back_btn")
