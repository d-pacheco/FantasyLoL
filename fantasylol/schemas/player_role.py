from enum import Enum


class PlayerRole(str, Enum):
    TOP = "top"
    JUNGLE = "jungle"
    MID = "mid"
    BOTTOM = "bottom"
    SUPPORT = "support"
    NONE = "none"
