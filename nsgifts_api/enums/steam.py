from enum import Enum


class SteamRegion(str, Enum):
    ...
# я хз че тут но что-то типа такого наверное
"""
    RU = "ru"
    KZ = "kz"
    UA = "ua"
    US = "us"
    EU = "eu"
"""


class SteamCurrency(str, Enum):
    RUB = "RUB"
    USD = "USD"


class SteamGiftType(str, Enum):
    GAME = "game"
    DLC = "dlc"
    PACKAGE = "package"
    SUBSCRIPTION = "subscription"
