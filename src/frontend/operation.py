import streamlit as st

from frontend.utils import change_menu_item
from frontend.general import create_big_button


def _back():
    st.button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "diagnosis_patient"})

def show_operation():
    person = st.session_state["current_patient_info"]
    st.title(f"🧪 Операция пациента {person.fio}")

    slices_status = getattr(person, "slices", None)
    t1_filled = bool(getattr(slices_status, "t1_filled", False)) if slices_status else False
    t2_filled = bool(getattr(slices_status, "t2_filled", False)) if slices_status else False
    t3_filled = bool(getattr(slices_status, "t3_filled", False)) if slices_status else False
    t4_filled = bool(getattr(slices_status, "t4_filled", False)) if slices_status else False
    t5_filled = bool(getattr(slices_status, "t5_filled", False)) if slices_status else False
    t6_filled = bool(getattr(slices_status, "t6_filled", False)) if slices_status else False
    t7_filled = bool(getattr(slices_status, "t7_filled", False)) if slices_status else False
    t8_filled = bool(getattr(slices_status, "t8_filled", False)) if slices_status else False

    col_t1_1, col_t1_2 = st.columns([2, 1])
    with col_t1_1:
        st.markdown(
            f"**Срез t1 - после индукции**  \nСтатус: {'✅ Заполнено' if t1_filled else '❌ Не заполнено'}"
        )
    with col_t1_2:
        create_big_button(
            "Перейти",
            on_click=change_menu_item,
            kwargs={"item": "show_t1_slice"},
            icon="📝",
            key="t1_btn",
        )

    col_t2_1, col_t2_2 = st.columns([2, 1])
    with col_t2_1:
        st.markdown(
            f"**Срез t2 - через 15 мин после эпидурального болюса**  \nСтатус: {'✅ Заполнено' if t2_filled else '❌ Не заполнено'}"
        )
    with col_t2_2:
        create_big_button(
            "Перейти",
            on_click=change_menu_item,
            kwargs={"item": "show_t2_slice"},
            icon="📝",
            key="t2_btn",
        )

    col_t3_1, col_t3_2 = st.columns([2, 1])
    with col_t3_1:
        st.markdown(
            f"**Срез t3 - после индукции анестезии и интубации трахеи**  \nСтатус: {'✅ Заполнено' if t3_filled else '❌ Не заполнено'}"
        )
    with col_t3_2:
        create_big_button(
            "Перейти",
            on_click=change_menu_item,
            kwargs={"item": "show_t3_slice"},
            icon="📝",
            key="t3_btn",
        )

    col_t4_1, col_t4_2 = st.columns([2, 1])
    with col_t4_1:
        st.markdown(
            f"**Срез t4 - после инсуффляции газа в брюшную полость**  \nСтатус: {'✅ Заполнено' if t4_filled else '❌ Не заполнено'}"
        )
    with col_t4_2:
        create_big_button(
            "Перейти",
            on_click=change_menu_item,
            kwargs={"item": "show_t4_slice"},
            icon="📝",
            key="t4_btn",
        )

    col_t5_1, col_t5_2 = st.columns([2, 1])
    with col_t5_1:
        st.markdown(
            f"**Срез t5 - в глубоком положении Тренделенбурга**  \nСтатус: {'✅ Заполнено' if t5_filled else '❌ Не заполнено'}"
        )
    with col_t5_2:
        create_big_button(
            "Перейти",
            on_click=change_menu_item,
            kwargs={"item": "show_t5_slice"},
            icon="📝",
            key="t5_btn",
        )

    col_t6_1, col_t6_2 = st.columns([2, 1])
    with col_t6_1:
        st.markdown(
            f"**Срез t6 - основной этап операции**  \nСтатус: {'✅ Заполнено' if t6_filled else '❌ Не заполнено'}"
        )
    with col_t6_2:
        create_big_button(
            "Перейти",
            on_click=change_menu_item,
            kwargs={"item": "show_t6_slice"},
            icon="📝",
            key="t6_btn",
        )

    col_t7_1, col_t7_2 = st.columns([2, 1])
    with col_t7_1:
        st.markdown(
            f"**Срез t7 - после десуффляции газа из брюшной полости**  \nСтатус: {'✅ Заполнено' if t7_filled else '❌ Не заполнено'}"
        )
    with col_t7_2:
        create_big_button(
            "Перейти",
            on_click=change_menu_item,
            kwargs={"item": "show_t7_slice"},
            icon="📝",
            key="t7_btn",
        )

    col_t8_1, col_t8_2 = st.columns([2, 1])
    with col_t8_1:
        st.markdown(
            f"**Срез t8 - сразу после экстубации трахеи**  \nСтатус: {'✅ Заполнено' if t8_filled else '❌ Не заполнено'}"
        )
    with col_t8_2:
        create_big_button(
            "Перейти",
            on_click=change_menu_item,
            kwargs={"item": "show_t8_slice"},
            icon="📝",
            key="t8_btn",
        )

    _back()


def show_postoperative():
    person = st.session_state["current_patient_info"]
    st.title(f"🏥 Послеоперационный период пациента {person.fio}")

    slices_status = getattr(person, "slices", None)
    t9_filled = bool(getattr(slices_status, "t9_filled", False)) if slices_status else False
    t10_filled = bool(getattr(slices_status, "t10_filled", False)) if slices_status else False

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            f"**Срез t9 - через час после перевода в АРО**  \nСтатус: {'✅ Заполнено' if t9_filled else '❌ Не заполнено'}"
        )
    with col2:
        create_big_button(
            "Перейти",
            on_click=change_menu_item,
            kwargs={"item": "show_t9_slice"},
            icon="📝",
            key="t9_btn",
        )

    col3, col4 = st.columns([2, 1])
    with col3:
        st.markdown(
            f"**Срез t10 - конец 1-х суток после операции**  \nСтатус: {'✅ Заполнено' if t10_filled else '❌ Не заполнено'}"
        )
    with col4:
        create_big_button(
            "Перейти",
            on_click=change_menu_item,
            kwargs={"item": "show_t10_slice"},
            icon="📝",
            key="t10_btn",
        )

    _back()


def show_operation_point():
    """Placeholder page for operation point."""
    st.title("⚙️ Операционный пункт")
    st.info("Раздел находится в разработке")
    _back()
