import time
from datetime import date

import streamlit as st

from database.functions import get_person, create_person, search_persons
from frontend.general import create_big_button
from frontend.scales.stopbang import _sb_risk_label
from frontend.utils import change_menu_item


def show_diagnosis_patient():
    person = get_person(st.session_state["current_patient_id"])
    st.title(f"🩺 Диагностика пациента {person.fio}")
    create_big_button(
        "Предоперационный осмотр",
        on_click=change_menu_item,
        kwargs={"item": "preoperative_exam"},
        icon="👁️")
    create_big_button(
        "Операция",
        on_click=change_menu_item,
        kwargs={"item": "operation"},
        icon="🧪")
    create_big_button(
        "Послеоперационный период",
        on_click=change_menu_item,
        kwargs={"item": "postoperative_period"},
        icon="🏥")
    create_big_button(
        "Выгрузить данные пациента",
        on_click=change_menu_item,
        kwargs={"item": "export_patient_data"},
        icon="📤")
    create_big_button("Назад", on_click=change_menu_item, kwargs={"item": "patients"}, icon="⬅️")


def add_patient():
    st.title("➕ Добавление пациента")
    with st.form("add_patient_form"):
        card_number = st.text_input("Номер карты")
        anesthesia_type = st.radio(
            "Тип анестезии",
            ["БОА", "ОА"],
            index=0,
            horizontal=True,
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            last_name = st.text_input("Фамилия")
        with c2:
            first_name = st.text_input("Имя")
        with c3:
            patronymic = st.text_input("Отчество")

        c4, c5 = st.columns(2)
        with c4:
            birth_date = st.date_input("Дата рождения", value=date(1990, 1, 1))
        with c5:
            inclusion_date = st.date_input("Дата включения", value=date.today())

        c6, c7, c8 = st.columns(3)
        with c6:
            height = st.number_input("Рост (см)", min_value=120, max_value=220, step=1, value=170)
        with c7:
            weight = st.number_input("Вес (кг)", min_value=20, max_value=260, step=1, value=80)
        with c8:
            gender_label = st.radio("Пол", ["Мужской", "Женский"], index=0, horizontal=True)

        gender = (gender_label == "Женский")  # False=мужской, True=женский

        try:
            bmi = weight / ((height / 100) ** 2)
            st.caption(f"ИМТ: **{bmi:.1f} кг/м²**")
        except Exception as er:
            print(er)

        submitted = st.form_submit_button("Добавить пациента", width='stretch')

    if submitted:
        if not last_name.strip() or not first_name.strip():
            st.error("Пожалуйста, укажите ФИО.")
            return
        p = create_person(
            card_number,
            anesthesia_type,
            last_name,
            first_name,
            patronymic,
            birth_date,
            inclusion_date,
            height,
            weight,
            gender,
        )
        st.success("Пациент добавлен!")
        time.sleep(0.3)
        st.session_state["current_patient_id"] = p.id
        st.session_state["current_patient_info"] = p
        change_menu_item(item="diagnosis_patient")
        st.rerun()

    create_big_button("Назад", on_click=change_menu_item, kwargs={"item": "patients"}, icon="⬅️")


def find_patient():
    st.title("🔍 Поиск пациента")

    # Форма ввода запроса
    with st.form("find_patient_form", clear_on_submit=False):
        q = st.text_input("Фамилия (или часть ФИО)", key="patients_find_q",
                          placeholder="Например: Иванов")
        submitted = st.form_submit_button("Искать", width='stretch')

    # При сабмите — фиксируем запрос и делаем rerun
    if submitted:
        q_fixed = (q or "").strip()
        if not q_fixed:
            st.warning("Введите хотя бы 1 символ для поиска.")
        else:
            st.session_state["patients_find_q_committed"] = q_fixed
            st.rerun()

    # Берём «зафиксированный» запрос
    q_committed = st.session_state.get("patients_find_q_committed", "").strip()

    # Рендерим результаты независимо от submitted
    if q_committed:
        results = search_persons(q_committed, limit=100)
        if not results:
            st.info("Ничего не найдено.")
        else:
            st.markdown(f"Найдено: **{len(results)}**")
            for p in results:
                col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
                with col1:
                    st.markdown(f"**{p.fio}**")
                    st.caption(f"Возраст: {p.age} • Рост: {p.height} см • Вес: {p.weight} кг")
                with col2:
                    st.caption("Пол")
                    st.write("Ж" if getattr(p, "gender", False) else "М")
                with col3:
                    st.caption("ИМТ")
                    try:
                        bmi = p.weight / ((p.height / 100) ** 2)
                        st.write(f"{bmi:.1f}")
                    except Exception:
                        st.write("—")
                with col4:
                    if st.button("Выбрать", key=f"pick_{p.id}"):
                        chosen = get_person(p.id)
                        st.session_state["current_patient_id"] = p.id
                        st.session_state["current_patient_info"] = chosen
                        change_menu_item(item="diagnosis_patient")
                        st.rerun()

    st.markdown("---")
    create_big_button("⬅️ Назад", on_click=change_menu_item,
                      kwargs={"item": "patients"}, key="back_from_search")


def export_patients():
    st.title("📤 Выгрузка всех пациентов")
    st.write("Здесь будет функционал для выгрузки всех пациентов.")
    create_big_button("Назад", on_click=change_menu_item, kwargs={"item": "patients"}, icon="⬅️")


def show_patients_menu():
    st.title("👩‍⚕️ Работа с пациентами")
    create_big_button("Добавить пациента", on_click=change_menu_item, kwargs={"item": "add_patient"}, icon="➕")
    create_big_button("Найти пациента", on_click=change_menu_item, kwargs={"item": "find_patient"}, icon="🔍")
    create_big_button(
        "Выгрузить всех пациентов",
        on_click=change_menu_item,
        kwargs={"item": "export_patients"},
        icon="📤")
    create_big_button("Назад", on_click=change_menu_item, kwargs={"item": "main"}, icon="⬅️")


def preoperative_exam():
    person = st.session_state["current_patient_info"]
    st.title(f"👁️ Предоперационный осмотр пациента {person.fio}")

    scales_status = getattr(person, "scales", None)
    slices_status = getattr(person, "slices", None)

    t0_filled = bool(getattr(slices_status, "t0_filled", False)) if slices_status else False
    col_t0_1, col_t0_2 = st.columns([2, 1])
    with col_t0_1:
        st.markdown(
            f"**Срез t0 -  на момент поступления**  \nСтатус: {'✅ Заполнено' if t0_filled else '❌ Не заполнено'}"
        )
    with col_t0_2:
        create_big_button(
            "Перейти",
            on_click=change_menu_item,
            kwargs={"item": "show_t0_slice"},
            icon="📝",
            key="t0_btn",
        )

    # ВАЖНО: разделили STOP-BANG и SOBA на отдельные строки
    scales = [
        ("Шкала El-Ganzouri — прогноз трудной интубации", "show_elganzouri_scale", "el_ganzouri_filled", "el_ganzouri"),
        ("Шкала ARISCAT — риск послеоперационных легочных осложнений", "show_ariscat_scale", "ariscat_filled",
         "ariscat"),
        ("Шкала STOP-BANG — скрининг СОАС", "show_stopbang_scale", "stopbang_filled", "stopbang"),
        ("Рекомендации SOBA — план ведения при ожирении", "show_soba_scale", "soba_filled", "soba"),
        ("Индекс Lee (RCRI) — оценка кардиального риска", "show_lee_scale", "lee_rcri_filled", "lee_rcri"),
        ("Шкала Caprini — оценка риска ВТЭО", "show_caprini_scale", "caprini_filled", "caprini"),
    ]

    for i, (label, item, status_field, rel_field) in enumerate(scales):
        col1, col2 = st.columns([2, 1])

        if not scales_status:
            status_text = "❌ Не заполнено"
        else:
            filled = bool(getattr(scales_status, status_field, False))
            if filled:
                rel_obj = getattr(scales_status, rel_field, None)
                if rel_obj is None:
                    status_text = "✅ Заполнено"
                else:
                    score = getattr(rel_obj, "total_score", None)
                    if rel_field == "stopbang":
                        risk = _sb_risk_label(getattr(rel_obj, "risk_level", None))
                        if score is not None and risk:
                            status_text = f"✅ Заполнено · Баллы: **{score}** · Риск: **{risk}**"
                        elif score is not None:
                            status_text = f"✅ Заполнено · Баллы: **{score}**"
                        else:
                            status_text = "✅ Заполнено"
                    else:
                        status_text = f"✅ Заполнено · Баллы: **{score}**" if score is not None else "✅ Заполнено"
            else:
                status_text = "❌ Не заполнено"

        with col1:
            st.markdown(f"**{label}**  \nСтатус: {status_text}")
        with col2:
            create_big_button(
                "Перейти",
                on_click=change_menu_item,
                kwargs={"item": item},
                icon="📊",
                key=f"scale_btn_{i}"
            )

    st.markdown("---")
    create_big_button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "diagnosis_patient"}, key="back_btn")
