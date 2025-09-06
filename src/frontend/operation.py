from datetime import datetime

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
    "chd_spontan": "ЧД спонтан (ед.)",
    "ofv1": "ОФВ1 (л/сек)",
    "fzhel": "ФЖЕЛ (л)",
    "foe": "ФОЕ (л)",
    "oel": "ОЕЛ (л)",
    "ool": "ООЛ (л)",
    "ofv1_fzhel": "ОФВ1/ФЖЕЛ (%)",
    "pos": "ПОС (%)",
    "mos25": "МОС25 (%)",
    "mos50": "МОС50 (%)",
    "mos75": "МОС75 (%)",
    "sos25_75": "СОС 25-75 (%)",
    "chss": "ЧСС (ед.)",
    "chss_min": "ЧСС мин (ед.)",
    "chss_max": "ЧСС макс (ед.)",
    "adsis": "АДсис (мм рт.ст.)",
    "adsis_min": "Адсис мин (мм рт.ст.)",
    "adsis_max": "Адсис макс (мм рт.ст.)",
    "addias": "АДдиас (мм рт.ст.)",
    "addias_min": "Аддиас мин (мм рт.ст.)",
    "addias_max": "Аддиас макс (мм рт.ст.)",
    "adsr": "АДср ((АД сис + 2хАДдиас)/3)",
    "adsr_min": "Адср мин ((АД сис + 2хАДдиас)/3)",
    "adsr_max": "Адср макс ((АД сис + 2хАДдиас)/3)",
    "spo2": "SpO2 (%)",
    "diurez_ml_h": "Диурез мл/ч (мл/ч)",
    "gemoglobin": "Гемоглобин (г/л)",
    "neytrofily": "Нейтрофилы (10^9)",
    "limfocity": "Лимфоциты (10^9)",
    "gematokrit": "Гематокрит (%)",
    "leykocity": "Лейкоциты (10^9)",
    "pya": "п/я (%)",
    "albumin": "Альбумин (г/л)",
    "kreatinin": "Креатинин (мкмоль/л)",
    "skf": "СКФ (мл/мин)",
    "nlr": "NLR",
    "glyukoza_krovi": "Глюкоза крови (ммоль/л)",
    "uo": "УО (мл)",
    "si": "СИ (л/мин/м2)",
    "iopss": "ИОПСС (дин.с.см-5)",
    "sao": "СаО (мл/л)",
    "do2": "DO2 (СаО * СИ)",
    "vbd": "ВБД (см вод ст)",
    "fio2": "FiO2 (%)",
    "etco2": "EtCO2 (мм рт ст)",
    "vt": "VT (мл)",
    "f": "f (1/мин)",
    "mv": "MV (VT * f, л)",
    "peep": "PEEP (см вод ст)",
    "ppik": "Pпик (см вод ст)",
    "rplato": "Рплато (см вод ст)",
    "delta_p": "ΔP (см вод ст)",
    "cstat": "Сstat (см вод ст)",
    "cdyn": "Cdyn (см вод ст)",
    "ball_uzl": "Балл УЗЛ (балл)",
    "mas": "МАС",
    "qcon": "qCon",
    "qnox": "qNOX",
    "emg": "EMG",
    "pn_arter": "Pн артер. (pH)",
    "be_arter": "BE артер. (ммоль/л)",
    "hco3_arter": "HCO3 артер. (ммоль/л)",
    "laktat_arter": "Лактат артер. (ммоль/л)",
    "rao2": "РаО2 (мм рт ст)",
    "rao2_fio2": "РаО2/FiO2 (мм рт ст)",
    "raso2": "РаСО2 (мм рт ст)",
    "sao2": "SаO2 (%)",
    "rin_prick": "Рin-prick (уровень)",
    "cold_test": "Cold-test (уровень)",
    "motorny_blok": "Моторный блок (баллы)",
    "t_operacii": "t операции (мин)",
    "t_probuzhdeniya": "t пробуждения (мин)",
    "t_do_extubacii": "t до экстубации (мин)",
    "obem_infuzia": "Объем инфузии (мл)",
    "polo": "ПОЛО",
    "frenikus_sind": "Френикус синд.",
    "frenikus_crsh": "Френикус/ ЦРШ (балл)",
    "opp": "ОПП (баллы)",
    "oslozhneniya": "Осложнения",
    "bol_crsh": "Боль/ ЦРШ (баллы)",
    "bol_crsh_min": "Боль/ ЦРШ Мин (баллы)",
    "bol_crsh_max": "Боль/ ЦРШ Макс (баллы)",
    "toshnota_rvota": "Тошнота/рвота (баллы)",
    "shkala_aldrete": "Шкала Aldrete (баллы)",
    "vremya_dost_aldrete": "Время достижения Aldrete 9-10 б. (ч.)",
    "t_aktivizacii": "t активизации (ч.)",
    "t_voss_peristalt": "t восс. перистал. (ч.)",
    "t_othozhd_gazov": "t отхожд. газов (ч.)",
    "rashod_opiatov": "Расход опиатов",
    "bol_mochev_cat": "Боль мочев кат (баллы)",
    "t_v_aro1": "t в АРО (1) (ч.)",
    "t_intensiv_boli": "t интенсив. боли (ч.)",
    "t_voss_foe": "t восс. ФОЕ (ч.)",
    "t_voss_skf": "t восс. СКФ (ч.)",
    "t_v_aro2": "t в АРО (2) (ч.)",
    "qor15": "QoR-15 (балл)",
    "udovletvoren": "Удовлетворен.",
}


def _split_label(label: str) -> tuple[str, str | None]:
    """Return label without units and unit placeholder if present."""
    if label.endswith(")"):
        depth = 0
        for i in range(len(label) - 1, -1, -1):
            ch = label[i]
            if ch == ")":
                depth += 1
            elif ch == "(":
                depth -= 1
                if depth == 0:
                    content = label[i + 1 : -1]
                    if content and not content.isdigit():
                        return label[:i].strip(), content
    parts = label.split()
    if len(parts) > 1:
        last = parts[-1]
        unit_candidate = last.strip().strip("()")
        if unit_candidate and not unit_candidate.isdigit() and (
            any(ch.isdigit() for ch in unit_candidate) or any(ch in "/%°" for ch in unit_candidate)
        ):
            return " ".join(parts[:-1]).strip(), unit_candidate
    return label, None


def _parse_date(value: str | None):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _parse_time(value: str | None):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        return None


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
            create_big_button(
                "Перейти",
                on_click=_open_point,
                kwargs={"point": p},
                key=f"open_{p}",
            )


def show_operation():
    person_id = st.session_state.get("current_patient_id")
    measures = op_get_points(person_id)
    st.title("🧪 Операция")
    _render_point_list(OPERATION_POINTS, measures)
    create_big_button(
        "Назад",
        on_click=change_menu_item,
        kwargs={"item": "diagnosis_patient"},
        icon="⬅️",
        key="back_operation",
    )


def show_postoperative():
    person_id = st.session_state.get("current_patient_id")
    measures = op_get_points(person_id)
    st.title("🏥 Послеоперационный период")
    _render_point_list(POSTOP_POINTS, measures)
    create_big_button(
        "Назад",
        on_click=change_menu_item,
        kwargs={"item": "diagnosis_patient"},
        icon="⬅️",
        key="back_postoperative",
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
        form_values: dict[str, str] = {}
        cols = st.columns(4)
        for i, (key, label) in enumerate(PARAMETERS.items()):
            base_label, placeholder = _split_label(label)
            with cols[i % 4]:
                if key == "date":
                    value = _parse_date(existing.get(key))
                    inp = st.date_input(base_label, value=value)
                    form_values[key] = inp.isoformat() if inp else ""
                elif key == "time":
                    value = _parse_time(existing.get(key))
                    inp = st.time_input(base_label, value=value)
                    form_values[key] = inp.strftime("%H:%M") if inp else ""
                else:
                    form_values[key] = st.text_input(
                        base_label, value=existing.get(key, ""), placeholder=placeholder
                    )
        submitted = st.form_submit_button("Сохранить", use_container_width=True)

    if submitted:
        data = {k: (v or None) for k, v in form_values.items()}
        op_save_point(person_id, OperationPointInput(point=point, data=data))
        st.success("Сохранено")

    back_item = "operation" if point in OPERATION_POINTS else "postoperative_period"
    create_big_button(
        "Назад",
        on_click=change_menu_item,
        kwargs={"item": back_item},
        icon="⬅️",
    )
