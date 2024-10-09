from enum import Enum


class FantasyPermissions(str, Enum):
    READ = "fantasy:Read"
    WRITE = "fantasy:Write"


class RiotPermissions(str, Enum):
    READ = "riot:Read"
    WRITE = "riot:Write"
