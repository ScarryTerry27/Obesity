from datetime import date, datetime

import streamlit as st


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
    if ftype == "int":
        return st.number_input(
            label,
            value=default if default is not None else 0,
            min_value=0,
            step=1,
            key=name,
        )
    return st.number_input(
        label,
        value=default if default is not None else 0.0,
        min_value=0.0,
        step=0.1,
        key=name,
    )


def render_slice_form(field_defs, defaults, form_key):
    with st.form(form_key):
        values = {}
        for i in range(0, len(field_defs), 4):
            cols = st.columns(4)
            for col, (name, label, placeholder, ftype) in zip(cols, field_defs[i : i + 4]):
                default = defaults.get(name)
                with col:
                    values[name] = _render_field(name, label, placeholder, ftype, default)
        submitted = st.form_submit_button("Сохранить", use_container_width=True)
    return values, submitted
