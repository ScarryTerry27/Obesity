import io
import time
from datetime import date

import pandas as pd
import streamlit as st

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

    if st.button("Сформировать выгрузку", use_container_width=True):
        persons = search_persons(limit=100000)
        if not persons:
            st.info("Нет данных для экспорта.")
            return

        scale_rows = []
        slice_rows = []
        for person in persons:
            atype = getattr(person, "anesthesia_type", None)
            base = {
                "patient_id": person.id,
                "№ карты": getattr(person, "card_number", ""),
                "Фамилия": getattr(person, "last_name", ""),
                "Имя": getattr(person, "first_name", ""),
                "Отчество": getattr(person, "patronymic", ""),
                "Дата включения": getattr(person, "inclusion_date", None),
                "Тип анестезии": atype.value if atype else "",
                "Возраст (лет)": getattr(person, "age", None),
                "Рост (см)": getattr(person, "height", None),
                "Вес (кг)": getattr(person, "weight", None),
                "Пол": "Ж" if bool(getattr(person, "gender", False)) else "М",
                "ИМТ": _bmi(getattr(person, "weight", None), getattr(person, "height", None)),
            }

            scale_row = base.copy()
            slice_row = base.copy()

            # Статусы заполнения шкал и срезов
            full = _safe(get_person, person.id, label="карточки пациента")
            scales_status = getattr(full, "scales", None) if full else None
            slices_status = getattr(full, "slices", None) if full else None

            if scales_status:
                scale_row.update({
                    "El-Ganzouri заполнена": bool(getattr(scales_status, "el_ganzouri_filled", False)),
                    "ARISCAT заполнена": bool(getattr(scales_status, "ariscat_filled", False)),
                    "STOP-BANG заполнена": bool(getattr(scales_status, "stopbang_filled", False)),
                    "SOBA заполнена": bool(getattr(scales_status, "soba_filled", False)),
                    "RCRI заполнена": bool(getattr(scales_status, "lee_rcri_filled", False)),
                    "Caprini заполнена": bool(getattr(scales_status, "caprini_filled", False)),
                    "Las Vegas заполнена": bool(getattr(scales_status, "las_vegas_filled", False)),
                    "Aldrete заполнена": bool(getattr(scales_status, "aldrete_filled", False)),
                    "MMSE t0 заполнена": bool(getattr(scales_status, "mmse_t0_filled", False)),
                    "MMSE t10 заполнена": bool(getattr(scales_status, "mmse_t10_filled", False)),
                    "QoR-15 заполнена": bool(getattr(scales_status, "qor15_filled", False)),
                })

            if slices_status:
                for idx in range(13):
                    slice_row[f"T{idx} заполнен"] = bool(getattr(slices_status, f"t{idx}_filled", False))

            elg = _safe(db_funcs.elg_get_result, person.id, label="El-Ganzouri")
            ar = _safe(db_funcs.ar_get_result, person.id, label="ARISCAT")
            sb = _safe(db_funcs.sb_get_result, person.id, label="STOP-BANG")
            soba = _safe(db_funcs.get_soba, person.id, label="SOBA")
            rcri = _safe(db_funcs.rcri_get_result, person.id, label="RCRI")
            cap = _safe(db_funcs.caprini_get_result, person.id, label="Caprini")
            lv = _safe(db_funcs.lv_get_result, person.id, label="Las Vegas")
            qor = _safe(db_funcs.qor15_get_result, person.id, label="QoR-15")
            ald = _safe(db_funcs.ald_get_result, person.id, label="Aldrete")
            mm0 = _safe(db_funcs.mmse_get_result, person.id, 0, label="MMSE t0")
            mm10 = _safe(db_funcs.mmse_get_result, person.id, 10, label="MMSE t10")

            def add_scale(prefix, obj):
                if obj is None:
                    return
                data = obj.model_dump()
                data.pop("id", None)
                data.pop("scales_id", None)
                score = data.pop("total_score", None)
                if score is not None:
                    scale_row[f"{prefix}: сумма"] = score
                for field, value in data.items():
                    scale_row[f"{prefix}: {field}"] = value

            add_scale("ELG", elg)
            if elg is not None:
                scale_row["ELG: рекомендация"] = _elg_plan(elg.total_score)

            add_scale("ARISCAT", ar)

            add_scale("STOP-BANG", sb)
            if sb is not None:
                scale_row["STOP-BANG: риск"] = _stopbang_label(getattr(sb, "risk_level", None))

            add_scale("SOBA", soba)
            if soba is not None:
                scale_row["SOBA: STOP-BANG риск (кэш)"] = _stopbang_label(getattr(soba, "stopbang_risk_cached", None))

            add_scale("RCRI", rcri)
            if rcri is not None:
                scale_row["RCRI: риск (частота осложнений)"] = _rcri_risk(rcri.total_score)

            add_scale("Caprini", cap)
            if cap is not None:
                scale_row["Caprini: риск"] = _caprini_label(getattr(cap, "risk_level", None))

            add_scale("Las Vegas", lv)
            if lv is not None:
                scale_row["Las Vegas: риск"] = _las_vegas_label(getattr(lv, "risk_level", None))

            add_scale("QoR-15", qor)

            add_scale("Aldrete", ald)

            add_scale("MMSE t0", mm0)
            add_scale("MMSE t10", mm10)

            scale_rows.append(scale_row)

            for idx in range(13):
                getter = getattr(db_funcs, f"t{idx}_get_result", None)
                data = _safe(getter, person.id, label=f"срез T{idx}") if getter else None
                if data is not None:
                    d = data.model_dump()
                    d.pop("id", None)
                    d.pop("slices_id", None)
                    for field, value in d.items():
                        slice_row[f"T{idx}: {field}"] = value

            slice_rows.append(slice_row)

        df_scales = pd.DataFrame(scale_rows)
        df_scales.replace({True: 1, False: 0}, inplace=True)

        df_slices = pd.DataFrame(slice_rows)
        df_slices.replace({True: 1, False: 0}, inplace=True)

        st.markdown("### Предпросмотр шкал")
        st.dataframe(df_scales, width="stretch")
        st.markdown("### Предпросмотр срезов")
        st.dataframe(df_slices, width="stretch")

        buf = io.BytesIO()
        with pd.ExcelWriter(buf) as writer:
            df_scales.to_excel(writer, index=False, sheet_name="Шкалы")
            df_slices.to_excel(writer, index=False, sheet_name="Срезы")

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
