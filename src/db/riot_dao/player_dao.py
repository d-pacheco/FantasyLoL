from sqlalchemy import func, label

from src.common.schemas.riot_data_schemas import ProfessionalPlayer, ProPlayerID
from src.db.models import ProfessionalPlayerModel, ProfessionalTeamModel, LeagueModel


def _player_query(session, join_league=False):
    query = session.query(
        ProfessionalPlayerModel.id,
        ProfessionalPlayerModel.team_id,
        ProfessionalPlayerModel.summoner_name,
        ProfessionalPlayerModel.first_name,
        ProfessionalPlayerModel.last_name,
        ProfessionalPlayerModel.image,
        ProfessionalPlayerModel.role,
        label("team_name", ProfessionalTeamModel.name),
        label("team_code", ProfessionalTeamModel.code),
    ).join(ProfessionalTeamModel, ProfessionalPlayerModel.team_id == ProfessionalTeamModel.id)
    if join_league:
        query = query.join(
            LeagueModel,
            func.lower(ProfessionalTeamModel.home_league_name) == func.lower(LeagueModel.name),
        )
    return query


def put_player(session, player: ProfessionalPlayer) -> None:
    db_player = ProfessionalPlayerModel(
        id=player.id,
        team_id=player.team_id,
        summoner_name=player.summoner_name,
        first_name=player.first_name,
        last_name=player.last_name,
        image=player.image,
        role=player.role,
    )
    session.merge(db_player)
    session.commit()


def get_players(
    session, filters: list | None = None, join_league: bool = False
) -> list[ProfessionalPlayer]:
    query = _player_query(session, join_league=join_league)
    if filters:
        query = query.filter(*filters)
    rows = query.all()
    return [ProfessionalPlayer.model_validate(row) for row in rows]


def get_player_by_id(session, player_id: ProPlayerID) -> ProfessionalPlayer | None:
    row = _player_query(session).filter(ProfessionalPlayerModel.id == player_id).first()
    if row is None:
        return None
    return ProfessionalPlayer.model_validate(row)
