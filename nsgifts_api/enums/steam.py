"""Steam-related enumerations."""

from enum import Enum


class Region(str, Enum):
    """Steam gift regions accepted by API v2."""

    RU = "ru"
    KZ = "kz"
    UA = "ua"
    CIS = "cis"
    CN = "cn"
