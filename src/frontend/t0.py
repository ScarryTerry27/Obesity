from datetime import date, datetime

import streamlit as st

from database.schemas.slice_t0 import SliceT0Input
from database.functions import t0_get_result, t0_upsert_result, get_person
from frontend.utils import change_menu_item
from frontend.components import create_big_button

FIELD_DEFS = [
    ("date", "Дата", "", "date"),
    ("time", "Время", "", "time"),
    ("rr_spont", "ЧД спонтан", "вдох/мин", "float"),
    ("fev1", "ОФВ1", "л", "float"),
    ("fvc", "ФЖЕЛ", "л", "float"),
    ("frc", "ФОЕ", "л", "float"),
    ("tlc", "ОЕЛ", "л", "float"),
    ("rv", "ООЛ", "л", "float"),
    ("fev1_fvc", "ОФВ1/ФЖЕЛ", "%", "float"),
    ("pef", "ПОС", "л/с", "float"),
    ("mef25", "МОС25", "л/с", "float"),
    ("mef50", "МОС50", "л/с", "float"),
    ("mef75", "МОС75", "л/с", "float"),
    ("fef25_75", "СОС 25-75", "л/с", "float"),
    ("heart_rate", "ЧСС", "уд/мин", "float"),
    ("sbp", "АДсис", "мм рт.ст.", "float"),
    ("dbp", "АДдиас", "мм рт.ст.", "float"),
    ("map", "АДср", "мм рт.ст.", "float"),
    ("spo2", "SpO2", "%", "float"),
    ("urine_ml_per_h", "Диурез мл/ч", "мл/ч", "float"),
    ("hemoglobin", "Гемоглобин", "г/л", "float"),
    ("neutrophils", "Нейтрофилы", "%", "float"),
    ("lymphocytes", "Лимфоциты", "%", "float"),
    ("hematocrit", "Гематокрит", "%", "float"),
    ("leukocytes", "Лейкоциты", "10^9/л", "float"),
    ("bands", "п/я", "%", "float"),
    ("albumin", "Альбумин", "г/л", "float"),
    ("creatinine", "Креатинин", "мкмоль/л", "float"),
    ("gfr", "СКФ", "мл/мин", "float"),
    ("nlr", "NLR", "", "float"),
    ("glucose", "Глюкоза крови", "ммоль/л", "float"),
    ("polo", "ПОЛО", "", "bool"),
    ("phrenic_syndrome", "Френикус синд.", "", "bool"),
    ("phrenic_crsh", "Френикус/ ЦРШ", "", "bool"),
    ("aki", "ОПП", "", "bool"),
    ("complications", "Осложнения", "", "str"),
    ("pain_nrs", "Боль/ ЦРШ", "баллы", "float"),
    ("pain_nrs_min", "Боль/ ЦРШ Мин", "баллы", "float"),
    ("pain_nrs_max", "Боль/ ЦРШ Макс", "баллы", "float"),
    ("nausea_vomiting", "Тошнота/рвота", "", "bool"),
    ("aldrete_score", "Шкала Aldrete", "баллы", "float"),
    ("aldrete_time", "Время достижения Aldrete 9-10 б.", "мин", "float"),
    ("t_activation", "t активизации", "ч", "float"),
    ("t_peristalsis", "t восс. перистал.", "ч", "float"),
    ("t_first_gas", "t отхожд. газов", "ч", "float"),
    ("opioid_consumption", "Расход опиатов", "мг", "float"),
    ("urinary_catheter_pain", "Боль мочев кат", "баллы", "float"),
    ("t_in_aro", "t в АРО", "ч", "float"),
    ("t_intense_pain", "t интенсив. боли", "ч", "float"),
    ("t_restore_frc", "t восс. ФОЕ", "ч", "float"),
    ("t_restore_gfr", "t восс. СКФ", "ч", "float"),
    ("t_in_ward", "t в стационаре", "ч", "float"),
    ("qor15", "QoR-15", "баллы", "float"),
    ("satisfied", "Удовлетворен.", "", "bool"),
]


def show_t0_slice():
    person = st.session_state["current_patient_info"]
    st.title(f"t0 показатели пациента {person.fio}")

    existing = t0_get_result(person.id)
    defaults = existing.model_dump() if existing else {}

    with st.form("t0_form"):
        values = {}
        for i in range(0, len(FIELD_DEFS), 4):
            cols = st.columns(4)
            for col, (name, label, placeholder, ftype) in zip(cols, FIELD_DEFS[i:i+4]):
                default = defaults.get(name)
                with col:
                    if ftype == "date":
                        val = st.date_input(label, value=default or date.today(), key=name)
                    elif ftype == "time":
                        val = st.time_input(label, value=default or datetime.now().time(), key=name)
                    elif ftype == "bool":
                        val = st.checkbox(label, value=bool(default), key=name)
                    elif ftype == "str":
                        val = st.text_input(label, value=default or "", placeholder=placeholder, key=name)
                    else:
                        val_str = st.text_input(label, value="" if default is None else str(default), placeholder=placeholder, key=name)
                        if val_str == "":
                            val = None
                        else:
                            try:
                                val = float(val_str.replace(',', '.'))
                            except ValueError:
                                val = None
                    values[name] = val
        submitted = st.form_submit_button("Сохранить", width='stretch')
    if submitted:
        t0_upsert_result(person.id, SliceT0Input(**values))
        st.session_state["current_patient_info"] = get_person(person.id)
        st.success("Данные сохранены")
        change_menu_item(item="preoperative_exam")
        st.rerun()
    create_big_button(
        "⬅️ Назад",
        on_click=change_menu_item,
        kwargs={"item": "preoperative_exam"},
        key="back_btn",
    )
