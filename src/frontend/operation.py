import streamlit as st

from frontend.utils import change_menu_item


def _back():
    st.button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "diagnosis_patient"})


def show_operation():
    """Placeholder page for operation details."""
    st.title("🧪 Операция")
    st.info("Раздел находится в разработке")
    _back()


def show_postoperative():
    """Placeholder page for postoperative period."""
    st.title("🏥 Послеоперационный период")
    st.info("Раздел находится в разработке")
    _back()


def show_operation_point():
    """Placeholder page for operation point."""
    st.title("⚙️ Операционный пункт")
    st.info("Раздел находится в разработке")
    _back()
