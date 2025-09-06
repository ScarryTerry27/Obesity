import streamlit as st

from database.functions import op_get_points, op_save_point
from database.schemas.operation import OperationPointInput, OperationPointRead
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


# Список всех параметров (ключ -> подпись)
PARAMETERS = {
    "date": "Дата",
    "time": "Время",
    "chd_spontan": "ЧД спонтан",
    "ofv1": "ОФВ1",
    "fzhel": "ФЖЕЛ",
    "foe": "ФОЕ",
    "oel": "ОЕЛ",
    "ool": "ООЛ",
    "ofv1_fzhel": "ОФВ1/ФЖЕЛ",
    "pos": "ПОС",
    "mos25": "МОС25",
    "mos50": "МОС50",
    "mos75": "МОС75",
    "sos25_75": "СОС 25-75",
    "chss": "ЧСС",
    "chss_min": "ЧСС мин",
    "chss_max": "ЧСС макс",
    "adsis": "АДсис",
    "adsis_min": "Адсис мин",
    "adsis_max": "Адсис макс",
    "addias": "АДдиас",
    "addias_min": "Аддиас мин",
    "addias_max": "Аддиас макс",
    "adsr": "АДср",
    "adsr_min": "Адср мин",
    "adsr_max": "Адср макс",
    "spo2": "SpO2",
    "diurez_ml_h": "Диурез мл/ч",
    "gemoglobin": "Гемоглобин",
    "neytrofily": "Нейтрофилы",
    "limfocity": "Лимфоциты",
    "gematokrit": "Гематокрит",
    "leykocity": "Лейкоциты",
    "pya": "п/я",
    "albumin": "Альбумин",
    "kreatinin": "Креатинин",
    "skf": "СКФ",
    "nlr": "NLR",
    "glyukoza_krovi": "Глюкоза крови",
    "uo": "УО",
    "si": "СИ",
    "iopss": "ИОПСС",
    "sao": "СаО",
    "do2": "DO2",
    "vbd": "ВБД",
    "fio2": "FiO2",
    "etco2": "EtCO2",
    "vt": "VT",
    "f": "f",
    "mv": "MV",
    "peep": "PEEP",
    "ppik": "Pпик",
    "rplato": "Рплато",
    "delta_p": "ΔP",
    "cstat": "Сstat",
    "cdyn": "Cdyn",
    "ball_uzl": "Балл УЗЛ",
    "mas": "МАС",
    "qcon": "qCon",
    "qnox": "qNOX",
    "emg": "EMG",
    "pn_arter": "Pн артер.",
    "be_arter": "BE артер.",
    "hco3_arter": "HCO3 артер.",
    "laktat_arter": "Лактат артер.",
    "rao2": "РаО2",
    "rao2_fio2": "РаО2/FiO2",
    "raso2": "РаСО2",
    "sao2": "SаO2",
    "rin_prick": "Рin-prick",
    "cold_test": "Cold-test",
    "motorny_blok": "Моторный блок",
    "t_operacii": "t операции",
    "t_probuzhdeniya": "t пробуждения",
    "t_do_extubacii": "t до экстубации",
    "obem_infuzia": "Объем инфузии",
    "polo": "ПОЛО",
    "frenikus_sind": "Френикус синд.",
    "frenikus_crsh": "Френикус/ ЦРШ",
    "opp": "ОПП",
    "oslozhneniya": "Осложнения",
    "bol_crsh": "Боль/ ЦРШ",
    "bol_crsh_min": "Боль/ ЦРШ Мин",
    "bol_crsh_max": "Боль/ ЦРШ Макс",
    "toshnota_rvota": "Тошнота/рвота",
    "shkala_aldrete": "Шкала Aldrete",
    "vremya_dost_aldrete": "Время достижения Aldrete 9-10 б.",
    "t_aktivizacii": "t активизации",
    "t_voss_peristalt": "t восс. перистал.",
    "t_othozhd_gazov": "t отхожд. газов",
    "rashod_opiatov": "Расход опиатов",
    "bol_mochev_cat": "Боль мочев кат",
    "t_v_aro1": "t в АРО (1)",
    "t_intensiv_boli": "t интенсив. боли",
    "t_voss_foe": "t восс. ФОЕ",
    "t_voss_skf": "t восс. СКФ",
    "t_v_aro2": "t в АРО (2)",
    "qor15": "QoR-15",
    "udovletvoren": "Удовлетворен.",
}


def _open_point(point: str):
    st.session_state["current_op_point"] = point
    change_menu_item(item="operation_point")


def _render_point_list(points: list[str], items: list[OperationPointRead]):
    status = {p: False for p in points}
    for m in items:
        if m.point in status and m.data:
            status[m.point] = True
    for p in points:
        col1, col2 = st.columns([2, 1])
        label = POINT_LABELS.get(p, p)
        text = "✅ Заполнено" if status[p] else "❌ Не заполнено"
        with col1:
            st.markdown(f"**{p} — {label}**  \nСтатус: {text}")
        with col2:
            create_big_button("Перейти", on_click=_open_point, kwargs={"point": p})


def show_operation():
    person_id = st.session_state.get("current_patient_id")
    measures = op_get_points(person_id)
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
    measures = op_get_points(person_id)
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
    all_points = {m.point: m for m in op_get_points(person_id)}
    current = all_points.get(point)
    title = "🧪 Операция" if point in OPERATION_POINTS else "🏥 Послеоперационный период"
    st.title(f"{title} — {POINT_LABELS.get(point, point)}")

    existing = current.data if current else {}

    with st.form("op_point_form"):
        form_values = {}
        for key, label in PARAMETERS.items():
            form_values[key] = st.text_input(label, value=existing.get(key, ""))
        submitted = st.form_submit_button("Сохранить", use_container_width=True)

    if submitted:
        data = {k: (v or None) for k, v in form_values.items()}
        op_save_point(person_id, OperationPointInput(point=point, data=data))
        st.success("Сохранено")
        st.rerun()

    back_item = "operation" if point in OPERATION_POINTS else "postoperative_period"
    create_big_button(
        "⬅️ Назад",
        on_click=change_menu_item,
        kwargs={"item": back_item},
        icon="⬅️",
    )
