from enum import Enum


class GameState(str, Enum):
    COMPLETED = "completed"
    INPROGRESS = "inProgress"
    UNSTARTED = "unstarted"
    UNNEEDED = "unneeded"
