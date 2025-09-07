import streamlit as st
from database.functions import rcri_get_result, rcri_upsert_result, get_person
from database.schemas.lee import LeeRcriInput
from frontend.components import create_big_button
from frontend.utils import change_menu_item


def _fmt_pct(x: float | int | None) -> str:
    if x is None:
        return "—"
    return f"{float(x):g}%"


def show_lee_scale():
    person = st.session_state.get("current_patient_info")
    if not person:
        st.error("Пациент не выбран.")
        return

    st.subheader("Индекс Lee (RCRI) — риск сердечно-сосудистых осложнений")

    # подтянем сохранённое (если есть)
    stored = rcri_get_result(person.id)

    if stored:
        st.info(
            f"Текущий результат: **{stored.total_score}** балл(ов) · "
            f"риск осложнений: **{_fmt_pct(stored.risk_percent)}**"
        )

    with st.form("lee_rcri_form"):
        c1, c2 = st.columns(2)
        with c1:
            high_risk_surgery = st.checkbox(
                "Операция высокого риска",
                value=bool(getattr(stored, "high_risk_surgery", False)),
            )
            ischemic_heart_disease = st.checkbox(
                "Ишемическая болезнь сердца",
                value=bool(getattr(stored, "ischemic_heart_disease", False)),
            )
            congestive_heart_failure = st.checkbox(
                "Хроническая сердечная недостаточность",
                value=bool(getattr(stored, "congestive_heart_failure", False)),
            )
        with c2:
            cerebrovascular_disease = st.checkbox(
                "ОНМК / ТИА в анамнезе",
                value=bool(getattr(stored, "cerebrovascular_disease", False)),
            )
            diabetes_on_insulin = st.checkbox(
                "Сахарный диабет на инсулине",
                value=bool(getattr(stored, "diabetes_on_insulin", False)),
            )
            creatinine_gt_180_umol_l = st.checkbox(
                "Креатинин > 180 мкмоль/л",
                value=bool(getattr(stored, "creatinine_gt_180_umol_l", False)),
            )

        submitted = st.form_submit_button("💾 Сохранить", width='stretch')

    if submitted:
        payload = LeeRcriInput(
            high_risk_surgery=high_risk_surgery,
            ischemic_heart_disease=ischemic_heart_disease,
            congestive_heart_failure=congestive_heart_failure,
            cerebrovascular_disease=cerebrovascular_disease,
            diabetes_on_insulin=diabetes_on_insulin,
            creatinine_gt_180_umol_l=creatinine_gt_180_umol_l,
        )
        saved = rcri_upsert_result(person.id, payload)

        st.success(
            f"Сохранено. Итог: **{saved.total_score}** балл(ов) · "
            f"риск осложнений: **{_fmt_pct(saved.risk_percent)}**"
        )
        st.session_state["current_patient_info"] = get_person(person.id)

    create_big_button("⬅️ Назад", on_click=change_menu_item,
                      kwargs={"item": "preoperative_exam"}, key="back_btn_lee")
