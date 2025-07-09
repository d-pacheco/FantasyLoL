from pydantic import BaseModel, ConfigDict


class PerkMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    styleId: int
    subStyleId: int
    perks: list[int]


class Participant(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    participantId: int
    level: int
    kills: int
    deaths: int
    assists: int
    totalGoldEarned: int
    creepScore: int
    killParticipation: float
    championDamageShare: float
    wardsPlaced: int
    wardsDestroyed: int
    attackDamage: int
    abilityPower: int
    criticalChance: float
    attackSpeed: int
    lifeSteal: int
    armor: int
    magicResistance: int
    tenacity: int
    items: list[int]
    perkMetadata: PerkMetadata
    abilities: list[str]


class DetailFrame(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rfc460Timestamp: str
    participants: list[Participant]


class GetLiveDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    frames: list[DetailFrame]
