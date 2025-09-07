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
from frontend.operation import show_operation, show_postoperative, show_operation_point
from frontend.t0 import show_t0_slice
from frontend.t1 import show_t1_slice
from frontend.t2 import show_t2_slice
from frontend.t3 import show_t3_slice
from frontend.t4 import show_t4_slice
from frontend.t5 import show_t5_slice
from frontend.t6 import show_t6_slice


menu_items = {
    "main": show_main_menu,
    "patients": show_patients_menu,
    "calculators": show_calculators_menu,
    "add_patient": add_patient,
    "find_patient": find_patient,
    "export_patients": export_patients,
    "diagnosis_patient": show_diagnosis_patient,
    "preoperative_exam": preoperative_exam,
    "operation": show_operation,
    "postoperative_period": show_postoperative,
    "operation_point": show_operation_point,
    "export_patient_data": export_patient_data,
    "show_elganzouri_scale": show_el_ganzouri_form,
    "show_ariscat_scale": show_ariscat_scale,
    "show_stopbang_scale": show_stopbang_scale,
    "show_soba_scale": show_soba_scale,
    "show_lee_scale": show_lee_scale,
    "show_caprini_scale": show_caprini_scale,
    "show_t0_slice": show_t0_slice,
    "show_t1_slice": show_t1_slice,
    "show_t2_slice": show_t2_slice,
    "show_t3_slice": show_t3_slice,
    "show_t4_slice": show_t4_slice,
    "show_t5_slice": show_t5_slice,
    "show_t6_slice": show_t6_slice,
}


def start_application():
    menu_items[st.session_state.get("stage", "main")]()


if __name__ == "__main__":
    settings()
    start_application()
