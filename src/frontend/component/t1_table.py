import pandas as pd
import streamlit as st

# Параметры для t1: (ключ, отображаемое имя, единица измерения)
T1_PARAMS = [
    ("date", "Дата", ""),
    ("time", "Время", ""),
    ("chd_spontan", "ЧД спонтан", "1/мин"),
    ("chss", "ЧСС", "уд/мин"),
    ("chss_min", "ЧСС мин", "уд/мин"),
    ("chss_max", "ЧСС макс", "уд/мин"),
    ("adsis", "АДсис", "мм рт.ст."),
    ("adsis_min", "Адсис мин", "мм рт.ст."),
    ("adsis_max", "Адсис макс", "мм рт.ст."),
    ("addias", "АДдиас", "мм рт.ст."),
    ("addias_min", "Аддиас мин", "мм рт.ст."),
    ("addias_max", "Аддиас макс", "мм рт.ст."),
    ("adsr", "АДср", "мм рт.ст."),
    ("adsr_min", "Адср мин", "мм рт.ст."),
    ("adsr_max", "Адср макс", "мм рт.ст."),
    ("spo2", "SpO2", "%"),
    ("diurez_ml_h", "Диурез мл/ч", "мл/ч"),
    ("gemoglobin", "Гемоглобин", "г/л"),
    ("uo", "УО", "мл"),
    ("si", "СИ", "л/мин/м²"),
    ("iopss", "ИОПСС", "дин·с·см⁻⁵·м²"),
    ("sao", "СаО", "мл O₂/дл"),
    ("do2", "DO2", "мл/мин"),
    ("vbd", "ВБД", "мм рт.ст."),
    ("fio2", "FiO2", "%"),
    ("ball_uzl", "Балл УЗЛ", "балл"),
    ("pn_arter", "Pн артер.", "мм рт.ст."),
    ("be_arter", "BE артер.", "ммоль/л"),
    ("hco3_arter", "HCO3 артер.", "ммоль/л"),
    ("laktat_arter", "Лактат артер.", "ммоль/л"),
    ("rao2", "РаО2", "мм рт.ст."),
    ("rao2_fio2", "РаО2/FiO2", "мм рт.ст."),
    ("raso2", "РаСО2", "мм рт.ст."),
    ("sao2", "SаO2", "%"),
    ("polo", "ПОЛО", "мл"),
    ("frenikus_sind", "Френикус синд.", "балл"),
    ("frenikus_crsh", "Френикус/ ЦРШ", "балл"),
    ("opp", "ОПП", "мл"),
    ("oslozhneniya", "Осложнения", ""),
    ("bol_crsh", "Боль/ ЦРШ", "балл"),
    ("bol_crsh_min", "Боль/ ЦРШ Мин", "балл"),
    ("bol_crsh_max", "Боль/ ЦРШ Макс", "балл"),
    ("toshnota_rvota", "Тошнота/рвота", "да/нет"),
    ("shkala_aldrete", "Шкала Aldrete", "балл"),
    ("vremya_dost_aldrete", "Время достижения Aldrete 9-10 б.", "мин"),
    ("t_aktivizacii", "t активизации", "ч"),
    ("t_voss_peristalt", "t восс. перистал.", "ч"),
    ("t_othozhd_gazov", "t отхожд. газов", "ч"),
    ("rashod_opiatov", "Расход опиатов", "мг"),
    ("bol_mochev_cat", "Боль мочев кат", "балл"),
    ("t_v_aro1", "t в АРО (1)", "ч"),
    ("t_intensiv_boli", "t интенсив. боли", "ч"),
    ("t_voss_foe", "t восс. ФОЕ", "ч"),
    ("t_voss_skf", "t восс. СКФ", "ч"),
    ("t_v_aro2", "t в АРО (2)", "ч"),
    ("qor15", "QoR-15", "балл"),
    ("udovletvoren", "Удовлетворен.", "да/нет"),
]


def create_t1_table():
    """Создаёт пустую таблицу t1 с многослойными заголовками."""
    columns = pd.MultiIndex.from_tuples([(label, unit) for _, label, unit in T1_PARAMS])
    return pd.DataFrame(columns=columns)


def show_t1_inputs():
    """Отображает форму для заполнения показателей t1 в 4 колонках."""
    st.header("Показатели t1")
    cols = st.columns(4)
    for idx, (key, label, unit) in enumerate(T1_PARAMS):
        col = cols[idx % 4]
        input_label = f"{label} ({unit})" if unit else label
        col.text_input(input_label, key=f"t1_{key}")

