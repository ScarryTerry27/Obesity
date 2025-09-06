import streamlit as st


def change_menu_item(item):
    st.session_state["stage"] = item
