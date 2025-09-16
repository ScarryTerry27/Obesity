from datetime import date, datetime

import streamlit as st

NUMERIC_LIMITS = {
    "albumin": (0, 100),
    "aldrete_score": (0, 10),
    "aldrete_time": (0, 600),
    "bands": (0, 100),
    "be_arterial": (-50, 50),
    "cao": (0, 30),
    "cardiac_index": (0, 10),
    "cdyn": (0, 100),
    "creatinine": (0, 1000),
    "cstat": (0, 100),
    "dbp": (0, 200),
    "dbp_max": (0, 200),
    "dbp_min": (0, 200),
    "delta_p": (0, 50),
    "do2": (0, 1000),
    "emg": (0, 100),
    "etco2": (0, 100),
    "f": (0, 100),
    "fef25_75": (0, 20),
    "fev1": (0, 10),
    "fev1_fvc": (0, 100),
    "fio2": (0, 100),
    "frc": (0, 10),
    "fvc": (0, 10),
    "gfr": (0, 200),
    "glucose": (0, 30),
    "hco3_arterial": (0, 50),
    "heart_rate": (0, 300),
    "heart_rate_max": (0, 300),
    "heart_rate_min": (0, 300),
    "hematocrit": (0, 100),
    "hemoglobin": (0, 250),
    "infusion_volume": (0, 10000),
    "lactate_arterial": (0, 20),
    "leukocytes": (0, 100),
    "lymphocytes": (0, 100),
    "mac": (0, 5),
    "map": (0, 300),
    "map_max": (0, 300),
    "map_min": (0, 300),
    "mef25": (0, 20),
    "mef50": (0, 20),
    "mef75": (0, 20),
    "motor_block": (0, 100),
    "mv": (0, 30),
    "neutrophils": (0, 100),
    "nlr": (0, 100),
    "opioid_consumption": (0, 1000),
    "paco2": (0, 200),
    "pain_nrs": (0, 10),
    "pain_nrs_max": (0, 10),
    "pain_nrs_min": (0, 10),
    "pao2": (0, 600),
    "pao2_fio2": (0, 1000),
    "peep": (0, 20),
    "pef": (0, 20),
    "ph_arterial": (0, 14),
    "pin_prick": (0, 100),
    "pn_arterial": (0, 200),
    "ppik": (0, 100),
    "qcon": (0, 10),
    "qnox": (0, 100),
    "qor15": (0, 150),
    "rplato": (0, 100),
    "rr_spont": (0, 100),
    "rv": (0, 10),
    "sao2": (0, 100),
    "sbp": (0, 300),
    "sbp_max": (0, 300),
    "sbp_min": (0, 300),
    "spo2": (0, 100),
    "stroke_volume": (0, 300),
    "svri": (0, 10000),
    "t_activation": (0, 1000),
    "t_awakening": (0, 1000),
    "t_before_extubation": (0, 1000),
    "t_first_gas": (0, 1000),
    "t_in_aro": (0, 1000),
    "t_in_ward": (0, 1000),
    "t_intense_pain": (0, 1000),
    "t_operation": (0, 1000),
    "t_peristalsis": (0, 1000),
    "t_restore_frc": (0, 1000),
    "t_restore_gfr": (0, 1000),
    "tlc": (0, 10),
    "urinary_catheter_pain": (0, 10),
    "urine_ml_per_h": (0, 1000),
    "uzl_score": (0, 10),
    "vbd": (0, 100),
    "vt": (0, 1000),
}

INT_FIELDS = {
    "rr_spont",
    "f",
    "heart_rate",
    "heart_rate_min",
    "heart_rate_max",
    "sbp",
    "sbp_min",
    "sbp_max",
    "dbp",
    "dbp_min",
    "dbp_max",
    "map",
    "map_min",
    "map_max",
    "spo2",
    "sao2",
    "urine_ml_per_h",
    "hemoglobin",
    "stroke_volume",
    "pain_nrs",
    "pain_nrs_min",
    "pain_nrs_max",
    "aldrete_score",
    "aldrete_time",
    "urinary_catheter_pain",
    "qor15",
    "uzl_score",
    "infusion_volume",
}


def create_big_button(label, on_click=None, kwargs=None, icon=None, key=None):
    st.button(label, on_click=on_click, kwargs=kwargs, width='stretch', icon=icon, key=key)


def _render_field(name, label, placeholder, ftype, default):
    if ftype == "date":
        return st.date_input(label, value=default or date.today(), key=name)
    if ftype == "time":
        return st.time_input(label, value=default or datetime.now().time(), key=name)
    if ftype == "bool":
        return st.checkbox(label, value=bool(default), key=name)
    if ftype == "str":
        return st.text_input(label, value=default or "", placeholder=placeholder, key=name)
    min_val, max_val = NUMERIC_LIMITS.get(name, (0, 1000))
    if ftype == "int":
        return st.number_input(
            label,
            value=default if default is not None else 0,
            min_value=int(min_val),
            max_value=int(max_val),
            step=1,
            key=name,
        )
    return st.number_input(
        label,
        value=default if default is not None else 0.0,
        min_value=float(min_val),
        max_value=float(max_val),
        step=0.1,
        key=name,
    )


def render_slice_form(field_defs, defaults, form_key):
    with st.form(form_key):
        values = {}
        for i in range(0, len(field_defs), 4):
            cols = st.columns(4)
            for col, (name, label, placeholder, ftype) in zip(cols, field_defs[i : i + 4]):
                if name in INT_FIELDS:
                    ftype = "int"
                default = defaults.get(name)
                with col:
                    values[name] = _render_field(name, label, placeholder, ftype, default)
        submitted = st.form_submit_button("Сохранить", use_container_width=True)
    return values, submitted
