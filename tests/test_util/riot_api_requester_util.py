import random
from fantasylol.schemas import riot_data_schemas as schemas
from fantasylol.schemas.game_state import GameState


class RiotApiRequesterUtil:
    # Fixtures:
    league_fixture = schemas.LeagueSchema(
        id=random.randint(100000, 999999),
        name="Mock Challengers",
        slug="mock-challengers-league",
        region="MOCKED REGION",
        image="http//:mocked-league-image.png",
        priority=1
    )

    tournament_fixture = schemas.TournamentSchema(
        id=random.randint(100000, 999999),
        slug="mock_slug_2023",
        start_date="2023-01-01",
        end_date="2023-02-03",
        league_id=league_fixture.id
    )

    team_1_fixture = schemas.ProfessionalTeamSchema(
        id=random.randint(100000, 999999),
        slug="mock-team-1",
        name="Mock Team 1",
        code="T1",
        image="http://mock-team-1-image.png",
        alternative_image="http://mock-team-1-alternative-image.png",
        background_image="http://mock-team-1-background.png",
        status="active",
        home_league=league_fixture.name
    )

    team_2_fixture = schemas.ProfessionalTeamSchema(
        id=random.randint(100000, 999999),
        slug="mock-team-2",
        name="Mock Team 2",
        code="T2",
        image="http://mock-team-2-image.png",
        alternative_image="http://mock-team-2-alternative-image.png",
        background_image="http://mock-team-2-background.png",
        status="active",
        home_league=league_fixture.name
    )

    match_fixture = schemas.MatchSchema(
        id=random.randint(100000, 999999),
        start_time="2023-01-03T15:00:00Z",
        block_name="mockBlockName",
        league_name=league_fixture.name,
        strategy_type="bestOf",
        strategy_count=3,
        tournament_id=tournament_fixture.id,
        team_1_name=team_1_fixture.name,
        team_2_name=team_2_fixture.name
    )

    game_1_fixture = schemas.GameSchema(
        id=random.randint(100000, 999999),
        state=GameState.COMPLETED,
        number=1,
        match_id=match_fixture.id
    )

    game_2_fixture = schemas.GameSchema(
        id=random.randint(100000, 999999),
        state=GameState.COMPLETED,
        number=2,
        match_id=match_fixture.id
    )

    game_3_fixture = schemas.GameSchema(
        id=random.randint(100000, 999999),
        state=GameState.UNNEEDED,
        number=3,
        match_id=match_fixture.id
    )

    player_1_fixture = schemas.ProfessionalPlayerSchema(
        id=random.randint(100000, 999999),
        summoner_name="MockerPlayer1",
        image="http://mocked-player-1.png",
        role="top",
        team_id=team_1_fixture.id
    )

    player_2_fixture = schemas.ProfessionalPlayerSchema(
        id=random.randint(100000, 999999),
        summoner_name="MockerPlayer2",
        image="http://mocked-player-2.png",
        role="jungle",
        team_id=team_1_fixture.id
    )

    player_3_fixture = schemas.ProfessionalPlayerSchema(
        id=random.randint(100000, 999999),
        summoner_name="MockerPlayer3",
        image="http://mocked-player-3.png",
        role="mid",
        team_id=team_1_fixture.id
    )

    player_4_fixture = schemas.ProfessionalPlayerSchema(
        id=random.randint(100000, 999999),
        summoner_name="MockerPlayer4",
        image="http://mocked-player-4.png",
        role="bottom",
        team_id=team_1_fixture.id
    )

    player_5_fixture = schemas.ProfessionalPlayerSchema(
        id=random.randint(100000, 999999),
        summoner_name="MockerPlayer5",
        image="http://mocked-player-5.png",
        role="support",
        team_id=team_1_fixture.id
    )

    # Responses:

    def get_leagues_mock_response(self):
        return {
            "data": {
                "leagues": [
                    {
                        "id": str(self.league_fixture.id),
                        "slug": self.league_fixture.slug,
                        "name": self.league_fixture.name,
                        "region": self.league_fixture.region,
                        "image": self.league_fixture.image,
                        "priority": self.league_fixture.priority,
                        "displayPriority": {
                            "position": 0,
                            "status": "selected"
                        }
                    }
                ]
            }
        }

    def get_tournaments_for_league_response(self):
        return {
            "data": {
                "leagues": [
                    {
                        "tournaments": [
                            {
                                "id": str(self.tournament_fixture.id),
                                "slug": self.tournament_fixture.slug,
                                "startDate": self.tournament_fixture.start_date,
                                "endDate": self.tournament_fixture.end_date
                            }
                        ]
                    }
                ]
            }
        }

    def get_teams_response(self):
        return {
            "data": {
                "teams": [
                    {
                        "id": str(self.team_1_fixture.id),
                        "slug": self.team_1_fixture.slug,
                        "name": self.team_1_fixture.name,
                        "code": self.team_1_fixture.code,
                        "image": self.team_1_fixture.image,
                        "alternativeImage": self.team_1_fixture.alternative_image,
                        "backgroundImage": self.team_1_fixture.background_image,
                        "status": self.team_1_fixture.status,
                        "homeLeague": {
                            "name": self.league_fixture.name,
                            "region": self.league_fixture.region
                        },
                        "players": [
                            {
                                "id": str(self.player_1_fixture.id),
                                "summonerName": self.player_1_fixture.summoner_name,
                                "firstName": "player_1_first_name",
                                "lastName": "player_1_last_name",
                                "image": self.player_1_fixture.image,
                                "role": self.player_1_fixture.role
                            },
                            {
                                "id": str(self.player_2_fixture.id),
                                "summonerName": self.player_2_fixture.summoner_name,
                                "firstName": "player_2_first_name",
                                "lastName": "player_2_last_name",
                                "image": self.player_2_fixture.image,
                                "role": self.player_2_fixture.role
                            },
                            {
                                "id": str(self.player_3_fixture.id),
                                "summonerName": self.player_3_fixture.summoner_name,
                                "firstName": "player_3_first_name",
                                "lastName": "player_3_last_name",
                                "image": self.player_3_fixture.image,
                                "role": self.player_3_fixture.role
                            },
                            {
                                "id": str(self.player_4_fixture.id),
                                "summonerName": self.player_4_fixture.summoner_name,
                                "firstName": "player_4_first_name",
                                "lastName": "player_4_last_name",
                                "image": self.player_4_fixture.image,
                                "role": self.player_4_fixture.role
                            },
                            {
                                "id": str(self.player_5_fixture.id),
                                "summonerName": self.player_5_fixture.summoner_name,
                                "firstName": "player_5_first_name",
                                "lastName": "player_5_last_name",
                                "image": self.player_5_fixture.image,
                                "role": self.player_5_fixture.role
                            },
                        ]
                    }
                ]
            }
        }

    def get_event_details_response(self):
        return {
            "data": {
                "event": {
                    "id": str(self.match_fixture.id),
                    "type": "match",
                    "tournament": {
                        "id": str(self.tournament_fixture.id)
                    },
                    "league": {
                        "id": str(self.league_fixture.id),
                        "slug": self.league_fixture.slug,
                        "image": self.league_fixture.image,
                        "name": self.league_fixture.name
                    },
                    "match": {
                        "strategy": {
                            "count": self.match_fixture.strategy_count
                        },
                        "teams": [
                            {
                                "id": str(self.team_1_fixture.id),
                                "name": self.team_1_fixture.name,
                                "code": self.team_1_fixture.code,
                                "image": self.team_1_fixture.image,
                                "result": {
                                    "gameWins": 2
                                }
                            },
                            {
                                "id": str(self.team_2_fixture.id),
                                "name": self.team_2_fixture.name,
                                "code": self.team_2_fixture.code,
                                "image": self.team_2_fixture.image,
                                "result": {
                                    "gameWins": 0
                                }
                            }
                        ],
                        "games": [
                            {
                                "number": self.game_1_fixture.number,
                                "id": str(self.game_1_fixture.id),
                                "state": self.game_1_fixture.state.value,
                                "teams": [
                                    {
                                        "id": str(self.team_1_fixture.id),
                                        "side": "blue"
                                    },
                                    {
                                        "id": str(self.team_2_fixture.id),
                                        "side": "red"
                                    }
                                ],
                                "vods": []
                            },
                            {
                                "number": self.game_2_fixture.number,
                                "id": str(self.game_2_fixture.id),
                                "state": self.game_2_fixture.state.value,
                                "teams": [
                                    {
                                        "id": str(self.team_1_fixture.id),
                                        "side": "blue"
                                    },
                                    {
                                        "id": str(self.team_2_fixture.id),
                                        "side": "red"
                                    }
                                ],
                                "vods": []
                            },
                            {
                                "number": self.game_3_fixture.number,
                                "id": str(self.game_3_fixture.id),
                                "state": self.game_3_fixture.state.value,
                                "teams": [
                                    {
                                        "id": str(self.team_2_fixture.id),
                                        "side": "blue"
                                    },
                                    {
                                        "id": str(self.team_1_fixture.id),
                                        "side": "red"
                                    }
                                ],
                                "vods": []
                            }
                        ]
                    },
                    "streams": []
                }
            }
        }
