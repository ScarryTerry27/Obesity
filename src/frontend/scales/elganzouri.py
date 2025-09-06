# ui_el_ganzouri.py
import streamlit as st

from database.functions import elg_get_result, elg_upsert_result, get_person
from database.schemas.elganzouri import ElGanzouriInput
from frontend.components import create_big_button
from frontend.utils import change_menu_item


def _elg_reco(total: int) -> str:
    if total <= 3:
        return "Интубация трахеи при обычной ларингоскопии"
    if total <= 7:
        return "Интубация трахеи при видеоларингоскопии"
    return "Интубация трахеи в сознании при бронхоскопии"


def show_el_ganzouri_form():
    st.subheader("Шкала El-Ganzouri")
    person = st.session_state.get("current_patient_info")
    if not person:
        st.error("Пациент не выбран.")
        return

    # 1) Текущий сохранённый результат (если есть)
    res = elg_get_result(person.id)

    defaults = {
        "interincisor_cm": 4.0,
        "thyromental_cm": 6.5,
        "neck_ext_deg": 90.0,
        "weight_kg": float(getattr(person, "weight", 90) or 90),
        "mallampati_raw": 2,
        "can_protrude": True,
        "diff_hx": "Нет",
    }
    if res:
        defaults.update({
            "interincisor_cm": res.interincisor_cm or defaults["interincisor_cm"],
            "thyromental_cm": res.thyromental_cm or defaults["thyromental_cm"],
            "neck_ext_deg": res.neck_ext_deg or defaults["neck_ext_deg"],
            "weight_kg": res.weight_kg or defaults["weight_kg"],
            "mallampati_raw": res.mallampati_raw or defaults["mallampati_raw"],
        })

    # 2) Форма
    mall_opts = {"I": 1, "II": 2, "III": 3, "IV": 4}
    inv_mall = {v: k for k, v in mall_opts.items()}

    with st.form("elg_form"):
        c1, c2 = st.columns(2)
        with c1:
            interincisor_cm = st.number_input(
                "Открывание рта (см)", 0.0, 10.0, step=0.1,
                value=float(defaults["interincisor_cm"])
            )
            thyromental_cm = st.number_input(
                "Тиреоментальное расстояние (см)", 0.0, 12.0, step=0.1,
                value=float(defaults["thyromental_cm"])
            )
            neck_ext_deg = st.number_input(
                "Экстензия шеи (°)", 0.0, 150.0, step=1.0,
                value=float(defaults["neck_ext_deg"])
            )
        with c2:
            weight_kg = st.number_input(
                "Масса тела (кг)", 20.0, 400.0, step=0.5,
                value=float(defaults["weight_kg"])
            )
            mall_disp = st.selectbox(
                "Маллампати", list(mall_opts.keys()),
                index=list(mall_opts.keys()).index(inv_mall.get(defaults["mallampati_raw"], "II"))
            )
            mallampati_raw = mall_opts[mall_disp]
            can_protrude = st.checkbox("Выдвижение нижней челюсти возможно", value=bool(defaults["can_protrude"]))
            diff_hx = st.selectbox("Трудная интубация в анамнезе", ["Нет", "Недостоверно", "Определенно"], index=0)

        submitted = st.form_submit_button("💾 Сохранить", use_container_width=True)

    # 3) Сохранение
    if submitted:
        data = ElGanzouriInput(
            interincisor_cm=interincisor_cm,
            thyromental_cm=thyromental_cm,
            neck_ext_deg=neck_ext_deg,
            weight_kg=weight_kg,
            mallampati_raw=mallampati_raw,
            can_protrude=can_protrude,
            diff_hx=diff_hx,
        )
        saved = elg_upsert_result(person.id, data)
        st.success(f"Сохранено. Сумма: **{saved.total_score}** · риск: **{_elg_reco(saved.total_score)}**")
        # обновим кэш пациента (для статусов в списке шкал)
        st.session_state["current_patient_info"] = get_person(person.id)

    create_big_button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "preoperative_exam"}, key="back_btn")
