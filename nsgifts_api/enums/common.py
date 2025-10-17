"""Common enumerations."""

from enum import Enum


class Region(str, Enum):
    """Steam regions.
    
    Attributes:
        RU: Russia
        KZ: Kazakhstan  
        UA: Ukraine
    """
    
    RU = "ru"
    KZ = "kz"
    UA = "ua"