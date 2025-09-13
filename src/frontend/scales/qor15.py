import streamlit as st

from database.functions import qor15_get_result, qor15_upsert_result, get_person
from database.schemas.qor15 import Qor15Input
from frontend.components import create_big_button
from frontend.utils import change_menu_item

# Each question is rated on an 11-point scale. Positive items (q1–q10)
# are scored from 0—"никогда" to 10—"всегда". Negative items
# (q11–q15) are scored from 0—"постоянно" to 10—"нет" so that
# higher scores always indicate better recovery.
QUESTIONS = [
    ("q1", "Способность легко дышать (0 — никогда, 10 — всегда)"),
    ("q2", "Способность получать удовольствие от еды (0 — никогда, 10 — всегда)"),
    ("q3", "Ощущение себя отдохнувшим (0 — никогда, 10 — всегда)"),
    ("q4", "Наличие хорошего сна (0 — никогда, 10 — всегда)"),
    ("q5", "Способность соблюдать личную гигиену без посторонней помощи (0 — никогда, 10 — всегда)"),
    ("q6", "Способность общаться с семьей или друзьями (0 — никогда, 10 — всегда)"),
    ("q7", "Получение поддержки от врачей и со стороны сестринского персонала (0 — никогда, 10 — всегда)"),
    ("q8", "Способность вернуться к работе или обычным домашним делам (0 — никогда, 10 — всегда)"),
    ("q9", "Ощущение комфорта и что всё под контролем (0 — никогда, 10 — всегда)"),
    ("q10", "Ощущение, что всё благополучно (0 — никогда, 10 — всегда)"),
    ("q11", "Умеренная боль (0 — постоянно, 10 — нет)"),
    ("q12", "Сильная боль (0 — постоянно, 10 — нет)"),
    ("q13", "Тошнота или рвота (0 — постоянно, 10 — нет)"),
    ("q14", "Чувство тревоги или беспокойства (0 — постоянно, 10 — нет)"),
    ("q15", "Чувство печали или подавленности (0 — постоянно, 10 — нет)"),
]


def show_qor15_scale():
    person = st.session_state.get("current_patient_info")
    if not person:
        st.error("Пациент не выбран.")
        return

    st.subheader("Шкала QoR-15")

    stored = qor15_get_result(person.id)
    if stored:
        st.info(f"Текущие данные: баллы **{stored.total_score}**")

    with st.form("qor15_form"):
        values = {}
        for field, label in QUESTIONS:
            values[field] = st.number_input(
                label,
                min_value=0,
                max_value=10,
                value=int(getattr(stored, field, 10)),
                step=1,
                key=field,
            )
        submitted = st.form_submit_button("💾 Сохранить", width='stretch')

    if submitted:
        data = Qor15Input(**values)
        saved = qor15_upsert_result(person.id, data)
        st.success(f"Сохранено. Баллы: **{saved.total_score}**")
        st.session_state["current_patient_info"] = get_person(person.id)
    create_big_button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "preoperative_exam"}, key="back_btn")
