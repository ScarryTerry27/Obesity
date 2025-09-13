import streamlit as st

from database.functions import ald_get_result, ald_upsert_result, get_person
from database.schemas.aldrete import AldreteInput
from frontend.components import create_big_button
from frontend.utils import change_menu_item


def show_aldrete_scale():
    person = st.session_state.get("current_patient_info")
    if not person:
        st.error("Пациент не выбран.")
        create_big_button(
            "⬅️ Назад",
            on_click=change_menu_item,
            kwargs={"item": "calculators"},
            key="back_btn",
        )
        return

    st.subheader("Шкала Aldrete — оценка выхода из анестезии")

    stored = ald_get_result(person.id)

    activity_opts = {
        "движение всеми конечностями по команде": 2,
        "движение двумя конечностями": 1,
        "не двигается": 0,
    }
    respiration_opts = {
        "глубокое дыхание и кашель": 2,
        "одышка/поверхностное дыхание": 1,
        "апноэ": 0,
    }
    pressure_opts = {
        "в пределах 20% до уровня перед анестезией": 2,
        "20–50% от исходного": 1,
        ">50% от исходного": 0,
    }
    consciousness_opts = {
        "ясное": 2,
        "пробуждается при обращении": 1,
        "не отвечает": 0,
    }
    spo2_opts = {
        ">92% на воздухе": 2,
        ">90% с кислородом": 1,
        "<90% с кислородом": 0,
    }

    act_vals = list(activity_opts.values())
    res_vals = list(respiration_opts.values())
    pr_vals = list(pressure_opts.values())
    con_vals = list(consciousness_opts.values())
    sp_vals = list(spo2_opts.values())

    act_idx = act_vals.index(getattr(stored, "activity_score", 2)) if getattr(stored, "activity_score", 2) in act_vals else 0
    res_idx = res_vals.index(getattr(stored, "respiration_score", 2)) if getattr(stored, "respiration_score", 2) in res_vals else 0
    pr_idx = pr_vals.index(getattr(stored, "pressure_score", 2)) if getattr(stored, "pressure_score", 2) in pr_vals else 0
    con_idx = con_vals.index(getattr(stored, "consciousness_score", 2)) if getattr(stored, "consciousness_score", 2) in con_vals else 0
    sp_idx = sp_vals.index(getattr(stored, "spo2_score", 2)) if getattr(stored, "spo2_score", 2) in sp_vals else 0

    if stored:
        st.info(f"Текущие данные: баллы **{stored.total_score}**")

    with st.form("aldrete_form"):
        activity_label = st.radio("Активность", list(activity_opts.keys()), index=act_idx)
        respiration_label = st.radio("Дыхание", list(respiration_opts.keys()), index=res_idx)
        pressure_label = st.radio("Артериальное давление", list(pressure_opts.keys()), index=pr_idx)
        consciousness_label = st.radio("Сознание", list(consciousness_opts.keys()), index=con_idx)
        spo2_label = st.radio("SpO₂", list(spo2_opts.keys()), index=sp_idx)
        submitted = st.form_submit_button("💾 Сохранить", width='stretch')

    if submitted:
        data = AldreteInput(
            activity_score=activity_opts[activity_label],
            respiration_score=respiration_opts[respiration_label],
            pressure_score=pressure_opts[pressure_label],
            consciousness_score=consciousness_opts[consciousness_label],
            spo2_score=spo2_opts[spo2_label],
        )
        saved = ald_upsert_result(person.id, data)
        st.success(f"Сохранено. Баллы: **{saved.total_score}**")
        st.session_state["current_patient_info"] = get_person(person.id)

    back_item = "preoperative_exam" if st.session_state.get("current_patient_info") else "calculators"
    create_big_button(
        "⬅️ Назад",
        on_click=change_menu_item,
        kwargs={"item": back_item},
        key="back_btn",
    )
