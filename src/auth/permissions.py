from enum import Enum


class Permissions(str, Enum):
    FANTASY_READ = "fantasy:Read"
    FANTASY_WRITE = "fantasy:Write"
    FANTASY_ADMIN = "fantasy:Admin"
    RIOT_READ = "riot:Read"
    RIOT_WRITE = "riot:Write"
    RIOT_ADMIN = "riot:Admin"
