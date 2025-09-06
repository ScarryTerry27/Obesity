from enum import Enum


class AriscatAge(Enum):
    LE_50 = 0  # ≤50
    BW_51_80 = 3  # 51-80
    GT_80 = 16  # >80


class AriscatSpO2(Enum):
    GE_96 = 0  # ≥96%
    BW_91_95 = 8  # 91-95%
    LE_90 = 24  # ≤90%


class AriscatRespInfect(Enum):
    NO = 0
    YES = 17  # респираторная инфекция за последний месяц


class AriscatAnemia(Enum):
    NO = 0
    YES = 11  # Hb ≤ 100 г/л


class AriscatIncision(Enum):
    PERIPHERAL = 0
    UPPER_ABD = 15  # верхний абдоминальный
    INTRATHORACIC = 24  # внутригрудной


class AriscatDuration(Enum):
    LT_2H = 0
    BW_2_3H = 16
    GT_3H = 23


class AriscatEmergency(Enum):
    NO = 0
    YES = 8
