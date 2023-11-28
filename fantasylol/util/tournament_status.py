from enum import Enum


class TournamentStatus(str, Enum):
    COMPLETED = "completed"
    ACTIVE = "active"
    UPCOMING = "upcoming"
