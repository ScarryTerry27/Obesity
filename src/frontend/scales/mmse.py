import streamlit as st

from database.functions import mmse_get_result, mmse_upsert_result, get_person
from database.schemas.mmse import MMSEInput
from frontend.components import create_big_button
from frontend.utils import change_menu_item

GROUPS = [
    ("ОРИЕНТАЦИИ", [
        ("orientation_date", "1. Какое сегодня число?"),
        ("orientation_month", "2. Какой сейчас месяц?"),
        ("orientation_year", "3. Какой сейчас год?"),
        ("orientation_weekday", "4. Какой сегодня день недели?"),
        ("orientation_season", "5. Какое сейчас время года?"),
        ("orientation_city", "6. В каком городе мы с Вами находимся?"),
        ("orientation_region", "7. В какой области мы находимся?"),
        ("orientation_institution", "8. Назовите учреждение, в котором Вы сейчас находитесь"),
        ("orientation_floor", "9. На каком этаже мы находимся?"),
        ("orientation_country", "10. В какой стране мы находимся?"),
    ]),
    ("Восприятие", [
        ("registration_ball1", "11. Ответил «Мяч» / «Карандаш»"),
        ("registration_ball2", "12. Ответил «Флаг» / «Дом»"),
        ("registration_ball3", "13. Ответил «Дверь» / «Копейка»"),
    ]),
    ("Внимание и счёт", [
        ("attention_93", "14. Правильно «93»"),
        ("attention_86", "15. Правильно «86»"),
        ("attention_79", "16. Правильно «79»"),
        ("attention_72", "17. Правильно «72»"),
        ("attention_65", "18. Правильно «65»"),
    ]),
    ("Память", [
        ("recall_ball1", "19. Ответил «Мяч» / «Карандаш»"),
        ("recall_ball2", "20. Ответил «Флаг» / «Дом»"),
        ("recall_ball3", "21. Ответил «Дверь» / «Копейка»"),
    ]),
    ("Речь", [
        ("language_clock", "22. Покажите пациенту часы и спросите «Что это?»"),
        ("language_pen", "23. Покажите пациенту ручку и спросите «Что это?»"),
        ("language_repeat", "24. Попросите пациента повторить «Не если, и, или нет»"),
    ]),
    ("Операция из 3 действий", [
        ("command_take_paper", "25. Пациент взял лист бумаги в правую руку"),
        ("command_fold_paper", "26. Пациент сложил пополам"),
        ("command_put_on_knee", "27. Пациент положил на колено"),
    ]),
    ("Чтение", [
        ("reading_close_eyes", "28. Пациент закрыл глаза"),
    ]),
    ("Письмо", [
        ("writing_sentence", "29. Пациент написал предложение"),
    ]),
    ("Копирование", [
        ("copying_pentagons", "30. Пациент перерисовал два пересекающихся пятиугольника."),
    ]),
]


def _show_form(timepoint: int, back_item: str, title: str):
    person = st.session_state.get("current_patient_info")
    if not person:
        st.error("Пациент не выбран.")
        return

    st.subheader(title)
    stored = mmse_get_result(person.id, timepoint)
    defaults = {name: bool(getattr(stored, name, False)) for group in GROUPS for name, _ in group[1]}

    # Инициализируем состояние чекбоксов сохранёнными значениями
    for group_name, items in GROUPS:
        for field, _ in items:
            key = f"{field}_{timepoint}"
            if key not in st.session_state:
                st.session_state[key] = defaults.get(field, False)

    if stored:
        st.info(f"Текущие данные: баллы **{stored.total_score}**")

    def _mark_all():
        for group_name, items in GROUPS:
            for field, _ in items:
                st.session_state[f"{field}_{timepoint}"] = True

    st.button("✅ Отметить все", on_click=_mark_all, key=f"mmse_mark_all_{timepoint}")

    with st.form(f"mmse_form_{timepoint}"):
        values = {}
        for group_name, items in GROUPS:
            st.markdown(f"**{group_name}**")
            for field, label in items:
                key = f"{field}_{timepoint}"
                values[field] = st.checkbox(label, key=key)
            st.write("")
        submitted = st.form_submit_button("💾 Сохранить", width='stretch')

    if submitted:
        data = MMSEInput(**values)
        saved = mmse_upsert_result(person.id, timepoint, data)
        st.success(f"Сохранено. Баллы: **{saved.total_score}**")
        st.session_state["current_patient_info"] = get_person(person.id)

    create_big_button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": back_item}, key=f"back_mmse_{timepoint}")


def show_mmse_t0():
    _show_form(0, "preoperative_exam", "MMSE до операции")


def show_mmse_t10():
    _show_form(10, "postoperative_period", "MMSE после операции")
