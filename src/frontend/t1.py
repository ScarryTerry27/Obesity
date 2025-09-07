from datetime import date, datetime

import streamlit as st

from database.schemas.slice_t1 import SliceT1Input
from database.functions import t1_get_result, t1_upsert_result
from frontend.utils import change_menu_item

FIELD_DEFS = [
    ("date", "Дата", "", "date"),
    ("time", "Время", "", "time"),
    ("rr_spont", "ЧД спонтан", "вдох/мин", "float"),
    ("heart_rate", "ЧСС", "уд/мин", "float"),
    ("heart_rate_min", "ЧСС мин", "уд/мин", "float"),
    ("heart_rate_max", "ЧСС макс", "уд/мин", "float"),
    ("sbp", "АДсис", "мм рт.ст.", "float"),
    ("sbp_min", "Адсис мин", "мм рт.ст.", "float"),
    ("sbp_max", "Адсис макс", "мм рт.ст.", "float"),
    ("dbp", "АДдиас", "мм рт.ст.", "float"),
    ("dbp_min", "Аддиас мин", "мм рт.ст.", "float"),
    ("dbp_max", "Аддиас макс", "мм рт.ст.", "float"),
    ("map", "АДср", "мм рт.ст.", "float"),
    ("map_min", "Адср мин", "мм рт.ст.", "float"),
    ("map_max", "Адср макс", "мм рт.ст.", "float"),
    ("spo2", "SpO2", "%", "float"),
    ("urine_ml_per_h", "Диурез мл/ч", "мл/ч", "float"),
    ("hemoglobin", "Гемоглобин", "г/л", "float"),
    ("stroke_volume", "УО", "мл", "float"),
    ("cardiac_index", "СИ", "л/мин/м²", "float"),
    ("svri", "ИОПСС", "дин·с·см⁻⁵·м²", "float"),
    ("cao2", "СаО", "мл/дл", "float"),
    ("do2", "DO2", "мл/мин", "float"),
    ("vbd", "ВБД", "мм рт.ст.", "float"),
    ("fio2", "FiO2", "доля", "float"),
    ("uzl_score", "Балл УЗЛ", "баллы", "float"),
    ("ph_arterial", "pH артер.", "", "float"),
    ("be_arterial", "BE артер.", "ммоль/л", "float"),
    ("hco3_arterial", "HCO3 артер.", "ммоль/л", "float"),
    ("lactate_arterial", "Лактат артер.", "ммоль/л", "float"),
    ("pao2", "РаО2", "мм рт.ст.", "float"),
    ("pao2_fio2", "РаО2/FiO2", "мм рт.ст.", "float"),
    ("paco2", "РаСО2", "мм рт.ст.", "float"),
    ("sao2", "SаO2", "%", "float"),
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


def show_t1_slice():
    person = st.session_state["current_patient_info"]
    st.title(f"t1 показатели пациента {person.fio}")

    existing = t1_get_result(person.id)
    defaults = existing.model_dump() if existing else {}

    with st.form("t1_form"):
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
        submitted = st.form_submit_button("Сохранить", use_container_width=True)
    if submitted:
        t1_upsert_result(person.id, SliceT1Input(**values))
        st.success("Данные сохранены")
        change_menu_item(item="postoperative_period")
        st.rerun()
    st.button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "postoperative_period"})
