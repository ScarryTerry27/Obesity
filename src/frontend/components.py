import streamlit as st


def create_big_button(label, on_click=None, kwargs=None, icon=None, key=None):
    st.button(label, on_click=on_click, kwargs=kwargs, use_container_width=True, icon=icon, key=key)
