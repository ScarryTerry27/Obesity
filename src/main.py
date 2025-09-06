import streamlit as st

from frontend.general import settings
from frontend.calculate import show_calculators_menu
from frontend.general import show_main_menu
from frontend.patient import (
    show_patients_menu,
    add_patient,
    find_patient,
    export_patients,
    show_diagnosis_patient,
    preoperative_exam
)
from frontend.scales.ariscat import show_ariscat_scale
from frontend.scales.caprini import show_caprini_scale
from frontend.scales.elganzouri import show_el_ganzouri_form
from frontend.scales.lee import show_lee_scale
from frontend.scales.soba import show_soba_scale
from frontend.scales.stopbang import show_stopbang_scale
from frontend.component.loader import export_patient_data


menu_items = {
    "main": show_main_menu,
    "patients": show_patients_menu,
    "calculators": show_calculators_menu,
    "add_patient": add_patient,
    "find_patient": find_patient,
    "export_patients": export_patients,
    "diagnosis_patient": show_diagnosis_patient,
    "preoperative_exam": preoperative_exam,
    "operation": lambda: st.write("Операция"),
    "postoperative_period": lambda: st.write("Послеоперационный период"),
    "export_patient_data": export_patient_data,
    "show_elganzouri_scale": show_el_ganzouri_form,
    "show_ariscat_scale": show_ariscat_scale,
    "show_stopbang_scale": show_stopbang_scale,
    "show_soba_scale": show_soba_scale,
    "show_lee_scale": show_lee_scale,
    "show_caprini_scale": show_caprini_scale
}


def start_application():
    menu_items[st.session_state.get("stage", "main")]()


if __name__ == "__main__":
    settings()
    start_application()
