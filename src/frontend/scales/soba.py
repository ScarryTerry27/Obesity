import streamlit as st
from database.schemas.soba import SobaCreate
from database.functions import (
    get_soba, upsert_soba, get_person, update_person_fields,
    sb_get_result,   # 👈 добавили импорт
)
from frontend.components import create_big_button
from frontend.utils import change_menu_item


def _risk_label(risk: int | None) -> str:
    if risk is None:
        return "—"
    return ["Низкий", "Промежуточный", "Высокий"][risk]


def show_soba_scale():
    person = st.session_state.get("current_patient_info")
    if not person:
        st.error("Пациент не выбран.")
        return

    st.subheader("SOBA — рекомендации при ожирении)")

    # 0) Требование: сначала должен быть рассчитан STOP-BANG
    sb = sb_get_result(person.id)
    if not sb:
        st.warning(
            "Сначала рассчитайте шкалу **STOP-BANG** — она нужна для контекста SOBA "
            "(оценка риска СОАС и принятие решений)."
        )
        create_big_button(
            "Перейти к STOP-BANG",
            on_click=change_menu_item,
            kwargs={"item": "show_stopbang_scale"},
            key="go_stopbang_btn",
            icon="🧮",
        )
        create_big_button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "preoperative_exam"}, key="back_btn")
        return

    # --- Текущие значения антропометрии из карточки пациента ---
    cur_height = int(person.height or 170)   # см
    cur_weight = int(person.weight or 90)    # кг

    stored = get_soba(person.id)

    with st.form("soba_form"):
        st.markdown("### Антропометрия")
        cb, cc = st.columns(2)
        with cb:
            new_height = st.number_input("Рост (см)", min_value=80, max_value=250, value=cur_height, step=1)
        with cc:
            new_weight = st.number_input("Вес (кг)", min_value=20, max_value=400, value=cur_weight, step=1)

        try:
            bmi = new_weight / ((new_height / 100) ** 2)
            st.caption(f"ИМТ: **{bmi:.1f} кг/м²**")
        except Exception:
            st.caption("ИМТ: —")

        st.markdown("### «Красные флаги» SOBA")
        c1, c2 = st.columns(2)
        with c1:
            poor_functional_status = st.checkbox(
                "Плохие функциональные данные",
                value=bool(getattr(stored, "poor_functional_status", False)),
            )
            ekg_changes = st.checkbox(
                "Изменения ЭКГ",
                value=bool(getattr(stored, "ekg_changes", False)),
            )
            uncontrolled_htn_ihd = st.checkbox(
                "Неконтролируемая АГ/ИБС",
                value=bool(getattr(stored, "uncontrolled_htn_ihd", False)),
            )
        with c2:
            spo2_room_air_lt_94 = st.checkbox(
                "SpO₂ < 94% (на воздухе)",
                value=bool(getattr(stored, "spo2_room_air_lt_94", False)),
            )
            hypercapnia_co2_gt_28 = st.checkbox(
                "Гиперкапния (PaCO₂ > 28)",
                value=bool(getattr(stored, "hypercapnia_co2_gt_28", False)),
            )
            vte_history = st.checkbox(
                "ТГВ/ТЭЛА в анамнезе",
                value=bool(getattr(stored, "vte_history", False)),
            )

        submitted = st.form_submit_button("💾 Сохранить", width='stretch')

    if submitted:
        # 1) обновим карточку пациента при изменениях
        changed = {}
        if new_height != cur_height:
            changed["height"] = int(new_height)
        if new_weight != cur_weight:
            changed["weight"] = int(new_weight)
        if changed:
            update_person_fields(person.id, **changed)

        # 2) сохраним SOBA
        payload = SobaCreate(
            poor_functional_status=poor_functional_status,
            ekg_changes=ekg_changes,
            uncontrolled_htn_ihd=uncontrolled_htn_ihd,
            spo2_room_air_lt_94=spo2_room_air_lt_94,
            hypercapnia_co2_gt_28=hypercapnia_co2_gt_28,
            vte_history=vte_history,
        )
        saved = upsert_soba(person.id, payload)

        # стоп-банг из кэша SOBA (сервис его подставляет)
        risk_label = _risk_label(getattr(saved, "stopbang_risk_cached", None))
        score = getattr(saved, "stopbang_score_cached", "—")
        st.success(f"SOBA сохранена. STOP-BANG: {score} баллов · риск: **{risk_label}**")

        # обновим пациента в сессии
        st.session_state["current_patient_info"] = get_person(person.id)

    create_big_button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "preoperative_exam"}, key="back_btn")