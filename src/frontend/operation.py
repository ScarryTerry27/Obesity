import pandas as pd
import streamlit as st

from database.functions import op_get_measures
from frontend.general import create_big_button
from frontend.utils import change_menu_item

OPERATION_POINTS = [f"T{i}" for i in range(0, 9)]  # T0-T8
POSTOP_POINTS = [f"T{i}" for i in range(9, 13)]  # T9-T12


def _pivot(measures, points):
    rows = [m.model_dump() for m in measures if m.point in points]
    if not rows:
        return None
    df = pd.DataFrame(rows)
    pivot = df.pivot_table(index="name", columns="point", values="value", aggfunc="first")
    pivot = pivot.sort_index(axis=1)
    return pivot


def show_operation():
    person_id = st.session_state.get("current_patient_id")
    measures = op_get_measures(person_id)
    st.title("🧪 Операция")
    table = _pivot(measures, OPERATION_POINTS)
    if table is None:
        st.info("Нет данных.")
    else:
        st.dataframe(table)
    create_big_button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "diagnosis_patient"}, icon="⬅️")


def show_postoperative():
    person_id = st.session_state.get("current_patient_id")
    measures = op_get_measures(person_id)
    st.title("🏥 Послеоперационный период")
    table = _pivot(measures, POSTOP_POINTS)
    if table is None:
        st.info("Нет данных.")
    else:
        st.dataframe(table)
    create_big_button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "diagnosis_patient"}, icon="⬅️")
