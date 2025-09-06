import streamlit as st

from frontend.components import create_big_button
from frontend.utils import change_menu_item


def show_main_menu():
    st.title("👩‍⚕️ Ассистент для подготовки к проведению анестезии")
    create_big_button("Пациенты", on_click=change_menu_item, kwargs={"item": "patients"}, icon="👩‍⚕️")
    create_big_button("Калькуляторы", on_click=change_menu_item, kwargs={"item": "calculators"}, icon="🧮")


def settings():
    if "stage" not in st.session_state:
        st.session_state["stage"] = "main"
    if "current_patient_id" not in st.session_state:
        st.session_state["current_patient_id"] = None
    if "current_patient_info" not in st.session_state:
        st.session_state["current_patient_info"] = None
