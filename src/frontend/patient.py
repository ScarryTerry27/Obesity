import io
import time
from datetime import date
from importlib import import_module

import pandas as pd
import streamlit as st
from functools import reduce

import database.functions as db_funcs
from database.functions import get_person, create_person, search_persons
from frontend.general import create_big_button
from frontend.scales.stopbang import _sb_risk_label
from frontend.utils import change_menu_item


def _safe(fetch_fn, *args, label="", default=None):
    """Безопасный вызов обёртки: ловим любые ошибки и показываем их в UI."""
    try:
        return fetch_fn(*args)
    except Exception as e:
        st.warning(f"⚠️ Ошибка при получении {label or fetch_fn.__name__}: {e}")
        return default


def _bmi(weight_kg, height_cm):
    try:
        if not weight_kg or not height_cm:
            return None
        h_m = float(height_cm) / 100.0
        if h_m <= 0:
            return None
        return round(float(weight_kg) / (h_m * h_m), 1)
    except Exception:
        return None


def _elg_plan(score):
    if score is None:
        return "—"
    if 0 <= score <= 3:
        return "Обычная ларингоскопия"
    if 4 <= score <= 7:
        return "Видеоларингоскопия"
    return "Интубация в сознании (бронхоскопия)"


def _stopbang_label(level):
    if level is None:
        return "—"
    return ["Низкий", "Промежуточный", "Высокий"][max(0, min(2, int(level)))]


def _caprini_label(level):
    if level is None:
        return "—"
    return [
        "Очень низкий",
        "Низкий",
        "Умеренный",
        "Высокий",
        "Очень высокий",
    ][max(0, min(4, int(level)))]


def _las_vegas_label(level):
    if level is None:
        return "—"
    return ["Низкий", "Промежуточный", "Высокий"][max(0, min(2, int(level)))]


def _rcri_risk(score):
    if score is None:
        return "—"
    if score == 0:
        return "≈0.4%"
    if score == 1:
        return "≈0.9%"
    if score == 2:
        return "≈7%"
    return "≈11%+"


def show_diagnosis_patient():
    person = get_person(st.session_state["current_patient_id"])
    st.title(f"🩺 Диагностика пациента {person.fio}")
    create_big_button(
        "Предоперационный осмотр",
        on_click=change_menu_item,
        kwargs={"item": "preoperative_exam"},
        icon="👁️")
    create_big_button(
        "Операция",
        on_click=change_menu_item,
        kwargs={"item": "operation"},
        icon="🧪")
    create_big_button(
        "Послеоперационный период",
        on_click=change_menu_item,
        kwargs={"item": "postoperative_period"},
        icon="🏥")
    create_big_button(
        "Выгрузить данные пациента",
        on_click=change_menu_item,
        kwargs={"item": "export_patient_data"},
        icon="📤")
    create_big_button("Назад", on_click=change_menu_item, kwargs={"item": "patients"}, icon="⬅️")


def add_patient():
    st.title("➕ Добавление пациента")
    with st.form("add_patient_form"):
        card_number = st.text_input("Номер карты")
        anesthesia_type = st.radio(
            "Тип анестезии",
            ["БОА", "ОА"],
            index=0,
            horizontal=True,
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            last_name = st.text_input("Фамилия")
        with c2:
            first_name = st.text_input("Имя")
        with c3:
            patronymic = st.text_input("Отчество")

        c4, c5 = st.columns(2)
        with c4:
            birth_date = st.date_input("Дата рождения", value=date(1990, 1, 1))
        with c5:
            inclusion_date = st.date_input("Дата включения", value=date.today())

        c6, c7, c8 = st.columns(3)
        with c6:
            height = st.number_input("Рост (см)", min_value=120, max_value=220, step=1, value=170)
        with c7:
            weight = st.number_input("Вес (кг)", min_value=20, max_value=260, step=1, value=80)
        with c8:
            gender_label = st.radio("Пол", ["Мужской", "Женский"], index=0, horizontal=True)

        gender = (gender_label == "Женский")  # False=мужской, True=женский

        try:
            bmi = weight / ((height / 100) ** 2)
            st.caption(f"ИМТ: **{bmi:.1f} кг/м²**")
        except Exception as er:
            print(er)

        submitted = st.form_submit_button("Добавить пациента", width='stretch')

    if submitted:
        if not last_name.strip() or not first_name.strip():
            st.error("Пожалуйста, укажите ФИО.")
            return
        p = create_person(
            card_number,
            anesthesia_type,
            last_name,
            first_name,
            patronymic,
            birth_date,
            inclusion_date,
            height,
            weight,
            gender,
        )
        st.success("Пациент добавлен!")
        time.sleep(0.3)
        st.session_state["current_patient_id"] = p.id
        st.session_state["current_patient_info"] = p
        change_menu_item(item="diagnosis_patient")
        st.rerun()

    create_big_button("Назад", on_click=change_menu_item, kwargs={"item": "patients"}, icon="⬅️")


def find_patient():
    st.title("🔍 Поиск пациента")

    with st.form("find_patient_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            last_name = st.text_input("Фамилия", key="patients_find_last_name")
        with col2:
            first_name = st.text_input("Имя", key="patients_find_first_name")
        with col3:
            patronymic = st.text_input("Отчество", key="patients_find_patronymic")

        col4, col5, col6 = st.columns(3)
        with col4:
            age_str = st.text_input("Возраст", key="patients_find_age")
        with col5:
            card_number = st.text_input("Номер истории", key="patients_find_card")
        with col6:
            inclusion_date = st.date_input("Дата добавления", value=None, key="patients_find_date")

        submitted = st.form_submit_button("Искать", width='stretch')

    if submitted:
        filters = {
            "last_name": (last_name or "").strip() or None,
            "first_name": (first_name or "").strip() or None,
            "patronymic": (patronymic or "").strip() or None,
            "card_number": (card_number or "").strip() or None,
            "inclusion_date": inclusion_date,
        }
        try:
            filters["age"] = int(age_str) if age_str.strip() else None
        except ValueError:
            st.warning("Возраст должен быть числом")
            filters["age"] = None
        st.session_state["patients_find_filters"] = filters
        st.rerun()

    filters = st.session_state.get("patients_find_filters")
    if filters:
        results = search_persons(limit=100, **filters)
        if not results:
            st.info("Ничего не найдено.")
        else:
            st.markdown(f"Найдено: **{len(results)}**")
            for p in results:
                col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
                with col1:
                    st.markdown(f"**{p.fio}**")
                    st.caption(f"Возраст: {p.age} • Рост: {p.height} см • Вес: {p.weight} кг")
                with col2:
                    st.caption("Пол")
                    st.write("Ж" if getattr(p, "gender", False) else "М")
                with col3:
                    st.caption("ИМТ")
                    try:
                        bmi = p.weight / ((p.height / 100) ** 2)
                        st.write(f"{bmi:.1f}")
                    except Exception:
                        st.write("—")
                with col4:
                    if st.button("Выбрать", key=f"pick_{p.id}"):
                        chosen = get_person(p.id)
                        st.session_state["current_patient_id"] = p.id
                        st.session_state["current_patient_info"] = chosen
                        change_menu_item(item="diagnosis_patient")
                        st.rerun()

    st.markdown("---")
    create_big_button("⬅️ Назад", on_click=change_menu_item,
                      kwargs={"item": "patients"}, key="back_from_search")


def export_patients():
    st.title("📤 Выгрузка всех пациентов")

    scale_map = {
        "El-Ganzouri": ("elg", lambda pid: db_funcs.elg_get_result(pid)),
        "ARISCAT": ("ariscat", lambda pid: db_funcs.ar_get_result(pid)),
        "STOP-BANG": ("stopbang", lambda pid: db_funcs.sb_get_result(pid)),
        "SOBA": ("soba", lambda pid: db_funcs.get_soba(pid)),
        "RCRI": ("rcri", lambda pid: db_funcs.rcri_get_result(pid)),
        "Caprini": ("caprini", lambda pid: db_funcs.caprini_get_result(pid)),
        "Las Vegas": ("las_vegas", lambda pid: db_funcs.lv_get_result(pid)),
        "QoR-15": ("qor15", lambda pid: db_funcs.qor15_get_result(pid)),
        "Aldrete": ("aldrete", lambda pid: db_funcs.ald_get_result(pid)),
        "MMSE t0": ("mmse_t0", lambda pid: db_funcs.mmse_get_result(pid, 0)),
        "MMSE t10": ("mmse_t10", lambda pid: db_funcs.mmse_get_result(pid, 10)),
    }
    slice_map = {f"T{i}": (f"t{i}", getattr(db_funcs, f"t{i}_get_result")) for i in range(13)}

    table_labels = ["Пациенты", "Статусы шкал"] + list(scale_map.keys()) + list(slice_map.keys())
    select_all = st.checkbox("Отметить все")
    selected = st.multiselect(
        "Выберите таблицы для выгрузки",
        table_labels,
        default=table_labels if select_all else [],
    )
    if select_all:
        selected = table_labels

    if st.button("Сформировать выгрузку", use_container_width=True):
        persons = search_persons(limit=100000)
        if not persons:
            st.info("Нет данных для экспорта.")
            return

        base_df = pd.DataFrame({"patient_id": [p.id for p in persons]})
        dfs = [base_df]

        if "Пациенты" in selected:
            patient_rows = []
            for person in persons:
                atype = getattr(person, "anesthesia_type", None)
                patient_rows.append(
                    {
                        "patient_id": person.id,
                        "card_number": getattr(person, "card_number", ""),
                        "last_name": getattr(person, "last_name", ""),
                        "first_name": getattr(person, "first_name", ""),
                        "patronymic": getattr(person, "patronymic", ""),
                        "inclusion_date": getattr(person, "inclusion_date", None),
                        "anesthesia_type": atype.value if atype else "",
                        "age": getattr(person, "age", None),
                        "height": getattr(person, "height", None),
                        "weight": getattr(person, "weight", None),
                        "gender": "Ж" if bool(getattr(person, "gender", False)) else "М",
                        "bmi": _bmi(getattr(person, "weight", None), getattr(person, "height", None)),
                    }
                )
            dfs.append(pd.DataFrame(patient_rows))

        if "Статусы шкал" in selected:
            status_rows = []
            for person in persons:
                full = _safe(get_person, person.id, label="карточки пациента")
                sc = getattr(full, "scales", None) if full else None
                row = {"patient_id": person.id}
                if sc:
                    for field in [
                        "el_ganzouri_filled",
                        "ariscat_filled",
                        "stopbang_filled",
                        "soba_filled",
                        "lee_rcri_filled",
                        "caprini_filled",
                        "las_vegas_filled",
                        "aldrete_filled",
                        "mmse_t0_filled",
                        "mmse_t10_filled",
                        "qor15_filled",
                    ]:
                        row[field] = bool(getattr(sc, field, False))
                status_rows.append(row)
            dfs.append(pd.DataFrame(status_rows))

        for label, (prefix, getter) in scale_map.items():
            if label not in selected:
                continue
            rows = []
            for person in persons:
                res = _safe(getter, person.id, label=label)
                row = {"patient_id": person.id}
                if res is not None:
                    data = res.model_dump()
                    data.pop("id", None)
                    data.pop("scales_id", None)
                    for k, v in data.items():
                        row[f"{prefix}_{k}"] = v
                rows.append(row)
            dfs.append(pd.DataFrame(rows))

        for label, (prefix, getter) in slice_map.items():
            if label not in selected:
                continue
            rows = []
            schema_module = import_module(f"database.schemas.slice_{prefix}")
            schema_cls = getattr(schema_module, f"Slice{prefix.upper()}Input")
            fields = list(schema_cls.model_fields.keys())
            for person in persons:
                res = _safe(getter, person.id, label=f"срез {label}")
                row = {"patient_id": person.id}
                for f in fields:
                    row[f"{prefix}_{f}"] = getattr(res, f, None) if res is not None else None
                rows.append(row)
            dfs.append(pd.DataFrame(rows))

        df_final = reduce(lambda l, r: pd.merge(l, r, on="patient_id", how="left"), dfs)
        df_final.replace({True: 1, False: 0}, inplace=True)

        st.markdown("### Предпросмотр")
        st.dataframe(df_final, width="stretch")

        buf = io.BytesIO()
        df_final.to_excel(buf, index=False)
        st.download_button(
            "⬇️ Скачать Excel",
            data=buf.getvalue(),
            file_name="patients_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    create_big_button("Назад", on_click=change_menu_item, kwargs={"item": "patients"}, icon="⬅️")


def show_patients_menu():
    st.title("👩‍⚕️ Работа с пациентами")
    create_big_button("Добавить пациента", on_click=change_menu_item, kwargs={"item": "add_patient"}, icon="➕")
    create_big_button("Найти пациента", on_click=change_menu_item, kwargs={"item": "find_patient"}, icon="🔍")
    create_big_button(
        "Выгрузить всех пациентов",
        on_click=change_menu_item,
        kwargs={"item": "export_patients"},
        icon="📤")
    create_big_button("Назад", on_click=change_menu_item, kwargs={"item": "main"}, icon="⬅️")


def preoperative_exam():
    person = st.session_state["current_patient_info"]
    st.title(f"👁️ Предоперационный осмотр пациента {person.fio}")

    scales_status = getattr(person, "scales", None)
    slices_status = getattr(person, "slices", None)

    t0_filled = bool(getattr(slices_status, "t0_filled", False)) if slices_status else False
    col_t0_1, col_t0_2 = st.columns([2, 1])
    with col_t0_1:
        st.markdown(
            f"**Срез t0 -  на момент поступления**  \nСтатус: {'✅ Заполнено' if t0_filled else '❌ Не заполнено'}"
        )
    with col_t0_2:
        create_big_button(
            "Перейти",
            on_click=change_menu_item,
            kwargs={"item": "show_t0_slice"},
            icon="📝",
            key="t0_btn",
        )

    mmse_t0_filled = bool(getattr(scales_status, "mmse_t0_filled", False)) if scales_status else False
    mmse_t0_score = None
    if mmse_t0_filled and scales_status:
        for r in getattr(scales_status, "mmse_results", []) or []:
            if getattr(r, "timepoint", None) == 0:
                mmse_t0_score = getattr(r, "total_score", None)
                break
    col_mmse1, col_mmse2 = st.columns([2, 1])
    with col_mmse1:
        status = (
            f"✅ Заполнено · Баллы: **{mmse_t0_score}**" if mmse_t0_score is not None else (
                "✅ Заполнено" if mmse_t0_filled else "❌ Не заполнено"
            )
        )
        st.markdown(f"**Шкала MMSE (t0) — когнитивный статус**  \\nСтатус: {status}")
    with col_mmse2:
        create_big_button(
            "Перейти",
            on_click=change_menu_item,
            kwargs={"item": "show_mmse_t0"},
            icon="📊",
            key="mmse_t0_btn",
        )

    # ВАЖНО: разделили STOP-BANG и SOBA на отдельные строки
    scales = [
        ("Шкала El-Ganzouri — прогноз трудной интубации", "show_elganzouri_scale", "el_ganzouri_filled", "el_ganzouri"),
        ("Шкала ARISCAT — риск послеоперационных легочных осложнений", "show_ariscat_scale", "ariscat_filled",
         "ariscat"),
        ("Шкала STOP-BANG — скрининг СОАС", "show_stopbang_scale", "stopbang_filled", "stopbang"),
        ("Рекомендации SOBA — план ведения при ожирении", "show_soba_scale", "soba_filled", "soba"),
        ("Индекс Lee (RCRI) — оценка кардиального риска", "show_lee_scale", "lee_rcri_filled", "lee_rcri"),
        ("Шкала Caprini — оценка риска ВТЭО", "show_caprini_scale", "caprini_filled", "caprini"),
        ("Шкала QoR-15 — качество восстановления", "show_qor15_scale", "qor15_filled", "qor15"),
        ("Шкала Aldrete — оценка выхода из анестезии", "show_aldrete_scale", "aldrete_filled", "aldrete"),
    ]

    for i, (label, item, status_field, rel_field) in enumerate(scales):
        col1, col2 = st.columns([2, 1])

        if not scales_status:
            status_text = "❌ Не заполнено"
        else:
            filled = bool(getattr(scales_status, status_field, False))
            if filled:
                rel_obj = getattr(scales_status, rel_field, None)
                if rel_obj is None:
                    status_text = "✅ Заполнено"
                else:
                    score = getattr(rel_obj, "total_score", None)
                    if rel_field == "stopbang":
                        risk = _sb_risk_label(getattr(rel_obj, "risk_level", None))
                        if score is not None and risk:
                            status_text = f"✅ Заполнено · Баллы: **{score}** · Риск: **{risk}**"
                        elif score is not None:
                            status_text = f"✅ Заполнено · Баллы: **{score}**"
                        else:
                            status_text = "✅ Заполнено"
                    else:
                        status_text = f"✅ Заполнено · Баллы: **{score}**" if score is not None else "✅ Заполнено"
            else:
                status_text = "❌ Не заполнено"

        with col1:
            st.markdown(f"**{label}**  \nСтатус: {status_text}")
        with col2:
            create_big_button(
                "Перейти",
                on_click=change_menu_item,
                kwargs={"item": item},
                icon="📊",
                key=f"scale_btn_{i}"
            )

    st.markdown("---")
    create_big_button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "diagnosis_patient"}, key="back_btn")
