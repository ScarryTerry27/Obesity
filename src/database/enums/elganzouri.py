from enum import Enum


class MouthOpening(Enum):  # Открывание рта
    GE_4_CM = 0  # ≥ 4 см
    LT_4_CM = 1  # < 4 см


class Thyromental(Enum):  # Тиреоментальное расстояние
    GT_6_5_CM = 0  # > 6.5 см
    BW_6_0_6_5 = 1  # 6.0–6.5 см
    LT_6_0_CM = 2  # < 6.0 см


class Mallampati(Enum):  # Класс по Маллампати (в статье до III)
    I = 0
    II = 1
    III = 2
    # При желании можно добавить IV = 2  # если придерживаемся 0/1/2 по протоколу центра


class NeckMobility(Enum):  # Подвижность шеи
    GT_90_DEG = 0  # > 90°
    BW_80_90 = 1  # 80–90°
    LT_80_DEG = 2  # < 80°


class MandibleProtrusion(Enum):  # Выдвижение нижней челюсти
    YES = 0
    NO = 1


class WeightBand(Enum):  # Масса тела
    LT_90_KG = 0
    KG_90_110 = 1
    GT_110_KG = 2


class DifficultIntubationHx(Enum):  # Трудная интубация в анамнезе
    NO = 0
    UNCERTAIN = 1  # «недостоверно»
    DEFINITE = 2  # «определенно»
