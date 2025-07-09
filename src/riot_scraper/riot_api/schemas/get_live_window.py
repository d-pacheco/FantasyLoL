from pydantic import BaseModel, ConfigDict
from src.common.schemas.riot_data_schemas import (
    PlayerRole,
    ProPlayerID,
    ProTeamID,
    RiotMatchID,
    RiotGameID,
    LiveGameState
)


class ParticipantMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    participantId: int
    esportsPlayerId: ProPlayerID
    summonerName: str
    championId: str
    role: PlayerRole


class TeamMetaData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    esportsTeamId: ProTeamID
    participantMetadata: list[ParticipantMetadata]


class GameMetaData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    patchVersion: str
    blueTeamMetadata: TeamMetaData
    redTeamMetadata: TeamMetaData


class ParticipantWindowFrame(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    participantId: int
    totalGold: int
    level: int
    kills: int
    deaths: int
    assists: int
    creepScore: int
    currentHealth: int
    maxHealth: int


class TeamWindowFrame(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    totalGold: int
    inhibitors: int
    towers: int
    barons: int
    totalKills: int
    dragons: list[str]
    participants: list[ParticipantWindowFrame]


class WindowFrame(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rfc460Timestamp: str
    gameState: LiveGameState
    blueTeam: TeamWindowFrame
    redTeam: TeamWindowFrame


class GetLiveWindowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    esportsGameId: RiotGameID
    esportsMatchId: RiotMatchID
    gameMetadata: GameMetaData
    frames: list[WindowFrame]
