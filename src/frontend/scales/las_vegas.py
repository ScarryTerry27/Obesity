import streamlit as st

from database.functions import lv_get_result, lv_upsert_result, get_person
from database.schemas.las_vegas import LasVegasInput
from frontend.components import create_big_button
from frontend.utils import change_menu_item


def _risk_label(level: int | None) -> str:
    if level is None:
        return "—"
    return ["Низкий", "Промежуточный", "Высокий"][max(0, min(2, int(level)))]


def show_las_vegas_scale():
    person = st.session_state.get("current_patient_info")
    if not person:
        st.error("Пациент не выбран.")
        return

    st.subheader("Шкала LAS VEGAS — оценка послеоперационного риска")

    stored = lv_get_result(person.id)

    age = int(getattr(stored, "age_years", getattr(person, "age", 50) or 50))
    asa_ps = int(getattr(stored, "asa_ps", 3))
    preop_spo2 = int(getattr(stored, "preop_spo2", 96))
    cancer = bool(getattr(stored, "cancer", False))
    osa = bool(getattr(stored, "osa", False))
    elective = bool(getattr(stored, "elective", True))
    duration = int(getattr(stored, "duration_minutes", 135))
    supraglottic = bool(getattr(stored, "supraglottic_device", False))
    anesthesia_type = getattr(stored, "anesthesia_type", "balanced")
    desaturation = bool(getattr(stored, "intraop_desaturation", False))
    vasoactives = bool(getattr(stored, "vasoactive_drugs", False))
    peep = float(getattr(stored, "peep_cm_h2o", 5.0))

    if stored:
        st.info(
            f"Текущие данные: баллы **{stored.total_score}** · риск **{_risk_label(stored.risk_level)}**"
        )

    with st.form("las_vegas_form"):
        age = st.number_input("Возраст (лет)", min_value=0, max_value=130, value=age, step=1)
        asa_ps = st.number_input("ASA PS", min_value=1, max_value=5, value=asa_ps, step=1)
        preop_spo2 = st.number_input("Предоперационная SpO₂ (%)", min_value=0, max_value=100, value=preop_spo2, step=1)
        cancer = st.checkbox("Онкологическое заболевание", value=cancer)
        osa = st.checkbox("Синдром обструктивного апноэ сна", value=osa)
        elective = st.checkbox("Плановая операция", value=elective)
        duration = st.number_input("Длительность операции (мин)", min_value=0, max_value=1000, value=duration, step=5)
        supraglottic = st.checkbox("Использовались надгортанные устройства", value=supraglottic)
        anesthesia_type = st.selectbox(
            "Тип анестезии",
            ["balanced", "tiva", "regional", "other"],
            index=["balanced", "tiva", "regional", "other"].index(anesthesia_type)
            if anesthesia_type in ["balanced", "tiva", "regional", "other"]
            else 0,
        )
        desaturation = st.checkbox("Десатурация во время операции", value=desaturation)
        vasoactives = st.checkbox("Потребность в вазоактивных препаратах", value=vasoactives)
        peep = st.number_input("ПДКВ (смH₂O)", min_value=0.0, max_value=20.0, value=peep, step=0.5)

        submitted = st.form_submit_button("💾 Сохранить", width='stretch')

    if submitted:
        data = LasVegasInput(
            age_years=age,
            asa_ps=asa_ps,
            preop_spo2=preop_spo2,
            cancer=cancer,
            osa=osa,
            elective=elective,
            duration_minutes=duration,
            supraglottic_device=supraglottic,
            anesthesia_type=anesthesia_type,
            intraop_desaturation=desaturation,
            vasoactive_drugs=vasoactives,
            peep_cm_h2o=peep,
        )
        saved = lv_upsert_result(person.id, data)
        st.success(
            f"Сохранено. Баллы: **{saved.total_score}** · риск: **{_risk_label(saved.risk_level)}**"
        )
        st.session_state["current_patient_info"] = get_person(person.id)

    create_big_button(
        "⬅️ Назад",
        on_click=change_menu_item,
        kwargs={"item": "postoperative_period"},
        key="back_btn",
    )
