from classy_fastapi import Routable, get
from fastapi import Query, Depends
from fastapi_pagination import paginate, Page

from src.auth import JWTBearer, Permissions
from src.common.schemas.riot_data_schemas import ProfessionalTeam, ProTeamID
from src.common.schemas.search_parameters import TeamSearchParameters
from src.riot.service import RiotProfessionalTeamService


class ProfessionalTeamEndpoint(Routable):
    def __init__(self, team_service: RiotProfessionalTeamService):
        super().__init__()
        self.__team_service = team_service

    @get(
        path="/professional-team",
        description="Get a list of professional teams based on a set of search criteria",
        tags=["Professional Teams"],
        dependencies=[Depends(JWTBearer([Permissions.RIOT_READ]))],
        response_model=Page[ProfessionalTeam],
        responses={
            200: {
                "model": Page[ProfessionalTeam]
            }
        }
    )
    def get_riot_professional_teams(
            self,
            slug: str = Query(None, description="Filter by professional teams slug"),
            name: str = Query(None, description="Filter by professional teams name"),
            code: str = Query(None, description="Filter by professional teams code"),
            status: str = Query(None, description="Filter by professional teams status"),
            league: str = Query(None, description="Filter by professional teams home league")
    ) -> Page[ProfessionalTeam]:
        search_parameters = TeamSearchParameters(
            slug=slug,
            name=name,
            code=code,
            status=status,
            league=league
        )
        teams = self.__team_service.get_teams(search_parameters)
        return paginate(teams)

    @get(
        path="/professional-team/{professional_team_id}",
        description="Get professional team by its ID",
        tags=["Professional Teams"],
        dependencies=[Depends(JWTBearer([Permissions.RIOT_READ]))],
        response_model=ProfessionalTeam,
        responses={
            200: {
                "model": ProfessionalTeam
            },
            404: {
                "description": "Not Found",
                "content": {
                    "application/json": {
                        "example": {"detail": "Professional Team not found"}
                    }
                }
            }
        }
    )
    def get_professional_team_by_id(
            self,
            professional_team_id: ProTeamID
    ) -> ProfessionalTeam:
        return self.__team_service.get_team_by_id(professional_team_id)
