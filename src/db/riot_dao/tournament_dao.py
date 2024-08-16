from typing import Optional, List

from src.common.schemas.riot_data_schemas import Tournament, RiotTournamentID
from src.db.models import TournamentModel


def put_tournament(session, tournament: Tournament) -> None:
    db_tournament = TournamentModel(**tournament.model_dump())
    session.merge(db_tournament)
    session.commit()


def get_tournaments(session, filters: list) -> List[Tournament]:
    if filters:
        query = session.query(TournamentModel).filter(*filters)
    else:
        query = session.query(TournamentModel)
    tournament_models: List[TournamentModel] = query.all()
    tournaments = [
        Tournament.model_validate(tournament_model)
        for tournament_model in tournament_models
    ]
    return tournaments


def get_tournament_by_id(session, tournament_id: RiotTournamentID) -> Optional[Tournament]:
    tournament_model: TournamentModel = session.query(TournamentModel) \
        .filter(TournamentModel.id == tournament_id).first()
    if tournament_model is None:
        return None
    else:
        return Tournament.model_validate(tournament_model)
