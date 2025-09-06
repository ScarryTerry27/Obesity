import pandas as pd
import streamlit as st

from database.functions import op_get_measures, op_add_measure
from database.schemas.operation import OperationDataInput, OperationDataRead
from frontend.general import create_big_button
from frontend.utils import change_menu_item

POINT_LABELS = {
    "T0": "на момент поступления",
    "T1": "на операционном столе",
    "T2": "через 15 мин после эпидурального болюса",
    "T3": "после индукции анестезии и интубации трахеи",
    "T4": "после инсуффляции газа в брюшную полость",
    "T5": "в глубоком положении Тренделенбурга",
    "T6": "основной этап операции",
    "T7": "после десуффляции газа из брюшной полости",
    "T8": "сразу после экстубации трахеи",
    "T9": "через час после перевода в АРО",
    "T10": "конец 1-х суток после операции",
    "T11": "конец 2-х суток после операции",
    "T12": "конец 5-х суток после операции",
}

OPERATION_POINTS = [f"T{i}" for i in range(0, 9)]
POSTOP_POINTS = [f"T{i}" for i in range(9, 13)]


def _open_point(point: str):
    st.session_state["current_op_point"] = point
    change_menu_item(item="operation_point")


def _render_point_list(points: list[str], measures: list[OperationDataRead]):
    status = {p: False for p in points}
    for m in measures:
        if m.point in status:
            status[m.point] = True
    for p in points:
        col1, col2 = st.columns([2, 1])
        label = POINT_LABELS.get(p, p)
        text = "✅ Заполнено" if status[p] else "❌ Не заполнено"
        with col1:
            st.markdown(f"**{p} — {label}**  \nСтатус: {text}")
        with col2:
            create_big_button(
                "Перейти",
                on_click=_open_point,
                kwargs={"point": p},
            )


def show_operation():
    person_id = st.session_state.get("current_patient_id")
    measures = op_get_measures(person_id)
    st.title("🧪 Операция")
    _render_point_list(OPERATION_POINTS, measures)
    create_big_button(
        "⬅️ Назад",
        on_click=change_menu_item,
        kwargs={"item": "diagnosis_patient"},
        icon="⬅️",
    )


def show_postoperative():
    person_id = st.session_state.get("current_patient_id")
    measures = op_get_measures(person_id)
    st.title("🏥 Послеоперационный период")
    _render_point_list(POSTOP_POINTS, measures)
    create_big_button(
        "⬅️ Назад",
        on_click=change_menu_item,
        kwargs={"item": "diagnosis_patient"},
        icon="⬅️",
    )


def show_operation_point():
    point = st.session_state.get("current_op_point")
    if not point:
        change_menu_item(item="operation")
        st.rerun()
    person_id = st.session_state.get("current_patient_id")
    measures = [m for m in op_get_measures(person_id) if m.point == point]
    title = "🧪 Операция" if point in OPERATION_POINTS else "🏥 Послеоперационный период"
    st.title(f"{title} — {POINT_LABELS.get(point, point)}")

    if measures:
        df = pd.DataFrame([m.model_dump() for m in measures])
        st.dataframe(df[["name", "value", "unit"]])
    else:
        st.info("Нет данных.")

    with st.form("op_point_form"):
        name = st.text_input("Параметр")
        value = st.text_input("Значение")
        unit = st.text_input("Ед. изм.")
        submitted = st.form_submit_button("Добавить", use_container_width=True)

    if submitted and name:
        data = OperationDataInput(point=point, name=name, value=value or None, unit=unit or None)
        op_add_measure(person_id, data)
        st.success("Сохранено")
        st.rerun()

    back_item = "operation" if point in OPERATION_POINTS else "postoperative_period"
    create_big_button(
        "⬅️ Назад",
        on_click=change_menu_item,
        kwargs={"item": back_item},
        icon="⬅️",
    )
