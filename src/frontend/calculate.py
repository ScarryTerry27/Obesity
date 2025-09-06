from frontend.general import create_big_button
import streamlit as st

from frontend.utils import change_menu_item


def show_calculators_menu():
    st.title("🧮 Калькуляторы")
    st.write("Здесь будет меню калькуляторов.")
    create_big_button("Назад", on_click=change_menu_item, kwargs={"item": "main"}, icon="⬅️")
