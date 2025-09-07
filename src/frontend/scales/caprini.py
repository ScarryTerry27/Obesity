import streamlit as st

from database.functions import (
    caprini_get_result,
    caprini_upsert_result,
    get_person,
    update_person_fields,  # 👈 понадобится для синхронизации Person
)
from database.schemas.caprini import CapriniInput
from frontend.components import create_big_button
from frontend.utils import change_menu_item


def _risk_label(level: int | None) -> str:
    # 0=оч. низкий, 1=низкий, 2=умеренный, 3=высокий
    if level is None:
        return "—"
    return ["Очень низкий", "Низкий", "Умеренный", "Высокий"][max(0, min(3, int(level)))]


def _bmi(weight_kg: float | int | None, height_cm: float | int | None) -> float | None:
    try:
        if not weight_kg or not height_cm:
            return None
        h_m = float(height_cm) / 100.0
        if h_m <= 0:
            return None
        return round(float(weight_kg) / (h_m * h_m), 1)
    except Exception:
        return None


def _caprini_age_bucket(age: int) -> tuple[str, int]:
    # возвращает (label, points)
    if age <= 40:
        return "≤40 лет", 0
    if 41 <= age <= 60:
        return "41–60 лет", 1
    if 61 <= age <= 74:
        return "61–74 лет", 2
    return "≥75 лет", 3


def show_caprini_scale():
    person = st.session_state.get("current_patient_info")
    if not person:
        st.error("Пациент не выбран.")
        return

    st.subheader("Шкала Caprini — риск ВТЭО")

    stored = caprini_get_result(person.id)

    # дефолты из карточки пациента
    def_age = int(getattr(person, "age", 40) or 40)
    def_height = int(getattr(person, "height", 170) or 170)
    def_weight = int(getattr(person, "weight", 90) or 90)

    # если уже считали — возьмём сохранённые «сырые» (приоритет)
    age_years = int(getattr(stored, "age_years", def_age) or def_age)
    height_cm = float(getattr(stored, "height_cm", def_height) or def_height)
    weight_kg = float(getattr(stored, "weight_kg", def_weight) or def_weight)

    # показать текущий итог, если уже есть
    if stored:
        st.info(f"Текущий итог: **{stored.total_score}** баллов · риск: **{_risk_label(stored.risk_level)}**")

    with st.form("caprini_form"):
        st.markdown("### Антропометрия")
        c0, c1, c2, c3 = st.columns([1, 1, 1, 1])
        with c1:
            age_years = st.number_input("Возраст (лет)", min_value=0, max_value=130, value=age_years, step=1)
        with c2:
            height_cm = st.number_input("Рост (см)", min_value=80.0, max_value=250.0, value=float(height_cm), step=1.0)
        with c3:
            weight_kg = st.number_input("Вес (кг)", min_value=20.0, max_value=400.0, value=float(weight_kg), step=1.0)

        bmi = _bmi(weight_kg, height_cm)
        st.caption(f"ИМТ: **{bmi:.1f} кг/м²**" if bmi is not None else "ИМТ: —")

        # === Возраст / ИМТ ===
        st.markdown("### Возраст / ИМТ")

        # определить дефолтный выбор возраста:
        # 1) если в сохранённом результате отмечены возрастные флаги — используем их
        # 2) иначе — вычисляем категорию по текущему age_years
        age_radio_options = ["≤40 лет (+0)", "41–60 лет (+1)", "61–74 лет (+2)", "≥75 лет (+3)"]

        stored_age_flags = {
            "41–60 лет (+1)": bool(getattr(stored, "age_41_60", False)),
            "61–74 лет (+2)": bool(getattr(stored, "age_61_74", False)),
            "≥75 лет (+3)": bool(getattr(stored, "age_ge_75", False)),
        }
        if any(stored_age_flags.values()):
            if stored_age_flags["41–60 лет (+1)"]:
                default_age_label = "41–60 лет (+1)"
            elif stored_age_flags["61–74 лет (+2)"]:
                default_age_label = "61–74 лет (+2)"
            else:
                default_age_label = "≥75 лет (+3)"
        else:
            # по текущему возрасту
            _label, _ = _caprini_age_bucket(int(age_years or 0))
            if _label == "≤40 лет":
                default_age_label = "≤40 лет (+0)"
            elif _label == "41–60 лет":
                default_age_label = "41–60 лет (+1)"
            elif _label == "61–74 лет":
                default_age_label = "61–74 лет (+2)"
            else:
                default_age_label = "≥75 лет (+3)"

        c_age, c_bmi = st.columns([2, 1])

        with c_age:
            age_choice = st.radio(
                "Возраст",
                options=age_radio_options,
                index=age_radio_options.index(default_age_label),
                horizontal=True,
            )
            # разложим radio в взаимно-исключающие флаги
            age_41_60 = (age_choice == "41–60 лет (+1)")
            age_61_74 = (age_choice == "61–74 лет (+2)")
            age_ge_75 = (age_choice == "≥75 лет (+3)")

        with c_bmi:
            bmi_gt_25 = st.checkbox(
                "ИМТ > 25 (+1)",
                value=bool(getattr(stored, "bmi_gt_25", (bmi or 0) > 25)),
            )
            st.caption("Отметьте, если ИМТ > 25 кг/м²")

        st.markdown("### Факторы (+1)")
        c1, c2 = st.columns(2)
        with c1:
            leg_swelling_now = st.checkbox("Отеки нижних конечностей",
                                           value=bool(getattr(stored, "leg_swelling_now", False)))
            varicose_veins = st.checkbox("Варикозные вены", value=bool(getattr(stored, "varicose_veins", False)))
            sepsis_lt_1m = st.checkbox("Сепсис (<1 мес)", value=bool(getattr(stored, "sepsis_lt_1m", False)))
            severe_lung_disease_lt_1m = st.checkbox("Тяжёлое заболевание лёгких (<1 мес)",
                                                    value=bool(getattr(stored, "severe_lung_disease_lt_1m", False)))
            ocp_or_hrt = st.checkbox("ОК / ГЗТ", value=bool(getattr(stored, "ocp_or_hrt", False)))
            pregnant_or_postpartum_lt_1m = st.checkbox("Беременность / послеродовой <1 мес",
                                                       value=bool(
                                                           getattr(stored, "pregnant_or_postpartum_lt_1m", False)))
            adverse_pregnancy_history = st.checkbox("Неблагопр. акушерский анамнез",
                                                    value=bool(getattr(stored, "adverse_pregnancy_history", False)))
        with c2:
            acute_mi = st.checkbox("Острый ИМ", value=bool(getattr(stored, "acute_mi", False)))
            chf_now_or_lt_1m = st.checkbox("ХСН (сейчас или <1 мес)",
                                           value=bool(getattr(stored, "chf_now_or_lt_1m", False)))
            bed_rest = st.checkbox("Постельный режим", value=bool(getattr(stored, "bed_rest", False)))
            ibd_history = st.checkbox("ВЗК в анамнезе", value=bool(getattr(stored, "ibd_history", False)))
            copd = st.checkbox("ХОБЛ", value=bool(getattr(stored, "copd", False)))
            minor_surgery = st.checkbox("Малое хирургическое вмешательство",
                                        value=bool(getattr(stored, "minor_surgery", False)))
            additional_risk_factor = st.checkbox("Доп. фактор риска",
                                                 value=bool(getattr(stored, "additional_risk_factor", False)))

        st.markdown("### Факторы (+2)")
        d1, d2 = st.columns(2)
        with d1:
            bed_rest_gt_72h = st.checkbox("Постельный режим >72 ч",
                                          value=bool(getattr(stored, "bed_rest_gt_72h", False)))
            major_surgery_lt_1m = st.checkbox("Большая хирургия <1 мес",
                                              value=bool(getattr(stored, "major_surgery_lt_1m", False)))
            cancer_current_or_past = st.checkbox("Злокачественное новообразование",
                                                 value=bool(getattr(stored, "cancer_current_or_past", False)))
            limb_immobilization_lt_1m = st.checkbox("Иммобилизация конечности <1 мес",
                                                    value=bool(getattr(stored, "limb_immobilization_lt_1m", False)))
        with d2:
            central_venous_catheter = st.checkbox("Центральный венозный катетер",
                                                  value=bool(getattr(stored, "central_venous_catheter", False)))
            arthroscopic_surgery = st.checkbox("Артроскопическая операция",
                                               value=bool(getattr(stored, "arthroscopic_surgery", False)))
            laparoscopy_gt_60m = st.checkbox("Лапароскопия >60 мин",
                                             value=bool(getattr(stored, "laparoscopy_gt_60m", False)))
            major_surgery_gt_45m = st.checkbox("Большая хирургия >45 мин",
                                               value=bool(getattr(stored, "major_surgery_gt_45m", False)))

        st.markdown("### Факторы (+3)")
        e1, e2 = st.columns(2)
        with e1:
            personal_vte_history = st.checkbox("Личный анамнез ВТЭО",
                                               value=bool(getattr(stored, "personal_vte_history", False)))
            factor_v_leiden = st.checkbox("Мутация фактора V (Лейден)",
                                          value=bool(getattr(stored, "factor_v_leiden", False)))
            prothrombin_20210a = st.checkbox("Мутация протромбина 20210A",
                                             value=bool(getattr(stored, "prothrombin_20210a", False)))
            lupus_anticoagulant = st.checkbox("Волчаночный антикоагулянт (+)",
                                              value=bool(getattr(stored, "lupus_anticoagulant", False)))
        with e2:
            family_vte_history = st.checkbox("Семейный анамнез ВТЭО",
                                             value=bool(getattr(stored, "family_vte_history", False)))
            hyperhomocysteinemia = st.checkbox("Гипергомоцистеинемия",
                                               value=bool(getattr(stored, "hyperhomocysteinemia", False)))
            hit = st.checkbox("Гепарин-индуцированная тромбоцитопения", value=bool(getattr(stored, "hit", False)))
            anticardiolipin_antibodies = st.checkbox("Антитела к кардиолипину (+)",
                                                     value=bool(getattr(stored, "anticardiolipin_antibodies", False)))
        other_thrombophilia = st.checkbox("Другая тромбофилия",
                                          value=bool(getattr(stored, "other_thrombophilia", False)))

        st.markdown("### Факторы (+5)")
        f1, f2 = st.columns(2)
        with f1:
            stroke_lt_1m = st.checkbox("Инсульт <1 мес", value=bool(getattr(stored, "stroke_lt_1m", False)))
            spinal_cord_injury_paralysis_lt_1m = st.checkbox("Повреждение спинного мозга с параличом <1 мес",
                                                             value=bool(
                                                                 getattr(stored, "spinal_cord_injury_paralysis_lt_1m",
                                                                         False)))
        with f2:
            multiple_trauma_lt_1m = st.checkbox("Множественные травмы <1 мес",
                                                value=bool(getattr(stored, "multiple_trauma_lt_1m", False)))
            major_joint_replacement = st.checkbox("Эндопротезирование крупных суставов",
                                                  value=bool(getattr(stored, "major_joint_replacement", False)))
            fracture_pelvis_or_limb = st.checkbox("Перелом таза/конечности",
                                                  value=bool(getattr(stored, "fracture_pelvis_or_limb", False)))

        submitted = st.form_submit_button("💾 Сохранить", width='stretch')

    if submitted:
        # 1) синхронизация с карточкой пациента (Person)
        person_age = int(getattr(person, "age", def_age) or def_age)
        person_height = int(getattr(person, "height", def_height) or def_height)
        person_weight = int(getattr(person, "weight", def_weight) or def_weight)

        changed = {}
        if int(height_cm) != person_height:
            changed["height"] = int(height_cm)
        if int(weight_kg) != person_weight:
            changed["weight"] = int(weight_kg)
        if changed:
            update_person_fields(person.id, **changed)

        # 2) сохраняем сам Caprini
        payload = CapriniInput(
            # сырые для автоподстановки возраста/ИМТ
            age_years=int(age_years),
            height_cm=float(height_cm),
            weight_kg=float(weight_kg),

            # явные флаги (радио/чекбокс)
            age_41_60=bool(age_41_60),
            age_61_74=bool(age_61_74),
            age_ge_75=bool(age_ge_75),
            bmi_gt_25=bool(bmi_gt_25),

            leg_swelling_now=bool(leg_swelling_now),
            varicose_veins=bool(varicose_veins),
            sepsis_lt_1m=bool(sepsis_lt_1m),
            severe_lung_disease_lt_1m=bool(severe_lung_disease_lt_1m),
            ocp_or_hrt=bool(ocp_or_hrt),
            pregnant_or_postpartum_lt_1m=bool(pregnant_or_postpartum_lt_1m),
            adverse_pregnancy_history=bool(adverse_pregnancy_history),
            acute_mi=bool(acute_mi),
            chf_now_or_lt_1m=bool(chf_now_or_lt_1m),
            bed_rest=bool(bed_rest),
            ibd_history=bool(ibd_history),
            copd=bool(copd),
            minor_surgery=bool(minor_surgery),
            additional_risk_factor=bool(additional_risk_factor),

            bed_rest_gt_72h=bool(bed_rest_gt_72h),
            major_surgery_lt_1m=bool(major_surgery_lt_1m),
            cancer_current_or_past=bool(cancer_current_or_past),
            limb_immobilization_lt_1m=bool(limb_immobilization_lt_1m),
            central_venous_catheter=bool(central_venous_catheter),
            arthroscopic_surgery=bool(arthroscopic_surgery),
            laparoscopy_gt_60m=bool(laparoscopy_gt_60m),
            major_surgery_gt_45m=bool(major_surgery_gt_45m),

            personal_vte_history=bool(personal_vte_history),
            factor_v_leiden=bool(factor_v_leiden),
            prothrombin_20210a=bool(prothrombin_20210a),
            lupus_anticoagulant=bool(lupus_anticoagulant),
            family_vte_history=bool(family_vte_history),
            hyperhomocysteinemia=bool(hyperhomocysteinemia),
            hit=bool(hit),
            anticardiolipin_antibodies=bool(anticardiolipin_antibodies),
            other_thrombophilia=bool(other_thrombophilia),

            stroke_lt_1m=bool(stroke_lt_1m),
            spinal_cord_injury_paralysis_lt_1m=bool(spinal_cord_injury_paralysis_lt_1m),
            multiple_trauma_lt_1m=bool(multiple_trauma_lt_1m),
            major_joint_replacement=bool(major_joint_replacement),
            fracture_pelvis_or_limb=bool(fracture_pelvis_or_limb),
        )

        saved = caprini_upsert_result(person.id, payload)
        st.success(f"Сохранено. Сумма: **{saved.total_score}** · Уровень риска: **{_risk_label(saved.risk_level)}**")

        # обновим карточку пациента в сессии, чтобы список шкал показал «Заполнено» и подтянул новые возраст/рост/вес
        st.session_state["current_patient_info"] = get_person(person.id)

    create_big_button("⬅️ Назад", on_click=change_menu_item, kwargs={"item": "preoperative_exam"}, key="back_btn")
