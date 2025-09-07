from datetime import date, datetime

import streamlit as st

from database.schemas.slice_t6 import SliceT6Input
from database.functions import t6_get_result, t6_upsert_result, get_person
from frontend.utils import change_menu_item


FIELD_DEFS = [
    ("date", "Дата", "", "date"),
    ("time", "Время", "", "time"),
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
    ("stroke_volume", "УО", "мл", "float"),
    ("cardiac_index", "СИ", "л/мин/м²", "float"),
    ("svri", "ИОПСС", "дин·с·см⁻⁵·м²", "float"),
    ("cao", "СаО", "мл/дл", "float"),
    ("do2", "DO2", "мл/мин", "float"),
    ("vbd", "ВБД", "", "float"),
    ("fio2", "FiO2", "%", "float"),
    ("etco2", "EtCO2", "мм рт.ст.", "float"),
    ("vt", "VT", "мл", "float"),
    ("f", "f", "1/мин", "float"),
    ("mv", "MV", "л/мин", "float"),
    ("peep", "PEEP", "см H2O", "float"),
    ("ppik", "Pпик", "см H2O", "float"),
    ("rplato", "Рплато", "см H2O", "float"),
    ("delta_p", "ΔP", "см H2O", "float"),
    ("cstat", "Сstat", "мл/см H2O", "float"),
    ("cdyn", "Cdyn", "мл/см H2O", "float"),
    ("uzl_score", "Балл УЗЛ", "баллы", "float"),
    ("mac", "МАС", "%", "float"),
    ("qcon", "qCon", "", "float"),
    ("qnox", "qNOX", "", "float"),
    ("emg", "EMG", "", "float"),
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


def show_t6_slice():
    person = st.session_state["current_patient_info"]
    st.title(f"t6 показатели пациента {person.fio}")
    st.caption("основной этап операции")

    existing = t6_get_result(person.id)
    defaults = existing.model_dump() if existing else {}

    with st.form("t6_form"):
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
                        val_str = st.text_input(
                            label,
                            value="" if default is None else str(default),
                            placeholder=placeholder,
                            key=name,
                        )
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
        t6_upsert_result(person.id, SliceT6Input(**values))
        st.session_state["current_patient_info"] = get_person(person.id)
        st.success("Данные сохранены")
        change_menu_item(item="operation")
        st.rerun()
    st.button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "operation"})
