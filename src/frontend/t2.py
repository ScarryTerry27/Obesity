import streamlit as st

from database.schemas.slice_t2 import SliceT2Input
from database.functions import t2_get_result, t2_upsert_result, get_person
from frontend.utils import change_menu_item
from frontend.components import create_big_button, render_slice_form

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
    ("stroke_volume", "УО", "мл", "float"),
    ("cardiac_index", "СИ", "л/мин/м²", "float"),
    ("svri", "ИОПСС", "дин·с·см⁻⁵·м²", "float"),
    ("cao", "СаО", "мл/дл", "float"),
    ("do2", "DO2", "мл/мин", "float"),
    ("vbd", "ВБД", "", "float"),
    ("fio2", "FiO2", "%", "float"),
    ("uzl_score", "Балл УЗЛ", "баллы", "float"),
    ("pin_prick", "Рin-prick", "", "bool"),
    ("cold_test", "Cold-test", "", "bool"),
    ("motor_block", "Моторный блок", "", "bool"),
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


def show_t2_slice():
    person = st.session_state["current_patient_info"]
    st.title(f"t2 показатели пациента {person.fio}")
    st.caption("через 15 мин после эпидурального болюса")

    existing = t2_get_result(person.id)
    defaults = existing.model_dump() if existing else {}

    values, submitted = render_slice_form(FIELD_DEFS, defaults, "t2_form")
    if submitted:
        t2_upsert_result(person.id, SliceT2Input(**values))
        st.session_state["current_patient_info"] = get_person(person.id)
        st.success("Данные сохранены")
        change_menu_item(item="operation")
        st.rerun()
    create_big_button(
        "⬅️ Назад",
        on_click=change_menu_item,
        kwargs={"item": "operation"},
        key="back_btn",
    )
