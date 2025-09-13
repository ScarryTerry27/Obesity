import streamlit as st

from database.functions import qor15_get_result, qor15_upsert_result, get_person
from database.schemas.qor15 import Qor15Input
from frontend.components import create_big_button
from frontend.utils import change_menu_item

QUESTIONS = [
    ("q1", "Способность легко дышать"),
    ("q2", "Способность получать удовольствие от еды"),
    ("q3", "Ощущение себя отдохнувшим"),
    ("q4", "Наличие хорошего сна"),
    ("q5", "Способность соблюдать личную гигиену без посторонней помощи"),
    ("q6", "Способность общаться с семьей или друзьями"),
    ("q7", "Получение поддержки от врачей и со стороны сестринского персонала"),
    ("q8", "Способность вернуться к работе или обычным домашним делам"),
    ("q9", "Ощущение комфорта и что всё под контролем"),
    ("q10", "Ощущение, что всё благополучно"),
    ("q11", "Умеренная боль"),
    ("q12", "Сильная боль"),
    ("q13", "Тошнота или рвота"),
    ("q14", "Чувство тревоги или беспокойства"),
    ("q15", "Чувство печали или подавленности"),
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
            values[field] = st.number_input(label, min_value=0, max_value=10, value=int(getattr(stored, field, 0)), step=1)
        submitted = st.form_submit_button("💾 Сохранить", width='stretch')

    if submitted:
        data = Qor15Input(**values)
        saved = qor15_upsert_result(person.id, data)
        st.success(f"Сохранено. Баллы: **{saved.total_score}**")
        st.session_state["current_patient_info"] = get_person(person.id)
    create_big_button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "preoperative_exam"}, key="back_btn")
