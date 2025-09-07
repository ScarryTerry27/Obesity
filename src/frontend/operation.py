import streamlit as st

from frontend.utils import change_menu_item
from frontend.general import create_big_button


def _back():
    st.button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "diagnosis_patient"})


def show_operation():
    """Placeholder page for operation details."""
    st.title("🧪 Операция")
    st.info("Раздел находится в разработке")
    _back()


def show_postoperative():
    """Postoperative period with t1 slice."""
    person = st.session_state["current_patient_info"]
    st.title(f"🏥 Послеоперационный период пациента {person.fio}")

    slices_status = getattr(person, "slices", None)
    t1_filled = bool(getattr(slices_status, "t1_filled", False)) if slices_status else False
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            f"**Срез t1**  \nСтатус: {'✅ Заполнено' if t1_filled else '❌ Не заполнено'}"
        )
    with col2:
        create_big_button(
            "Перейти",
            on_click=change_menu_item,
            kwargs={"item": "show_t1_slice"},
            icon="📝",
            key="t1_btn",
        )

    st.markdown("---")
    _back()


def show_operation_point():
    """Placeholder page for operation point."""
    st.title("⚙️ Операционный пункт")
    st.info("Раздел находится в разработке")
    _back()
