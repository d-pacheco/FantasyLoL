import random
from db.models import Game
from db.models import ProfessionalTeam
from db.models import League
from db.models import Tournament


class RiotApiRequestUtil:

    mock_league_id = str(random.randint(100000, 999999))
    mock_league_name = "Mock Challengers"
    mock_league_slug = "mock-challengers-league"
    mock_league_region = "MOCKED REGION"
    mock_league_image = "http/mocked-league-image.png"

    mock_tournament_id = str(random.randint(100000, 999999))
    mock_tournament_slug = "mock_slug_2023"
    mock_tournament_start_date = "2023-01-01"
    mock_tournament_end_date = "2023-02-03"

    mock_match_id = str(random.randint(100000, 999999))

    mock_team_1_id = str(random.randint(100000, 999999))
    mock_team_1_name = "Mock Team 1"
    mock_team_1_slug = "mock-team-1"
    mock_team_1_code = "TEST1"
    mock_team_1_image = "http://test-team-1-image"
    mock_team_1_alt_image = ""
    mock_team_1_background_image = "http://mocked-team-1-background.png"
    mock_team_1_status = "active"

    mock_team_2_id = str(random.randint(100000, 999999))
    mock_team_2_name = "Mock Team 2"
    mock_team_2_slug = "mock-team-2"
    mock_team_2_code = "TEST2"
    mock_team_2_image = "http://test-team-2-image"
    mock_team_2_alt_image = "http://mocked-team-2-alternative.png"
    mock_team_2_background_image = "http://mocked-team-2-background.png"
    mock_team_2_status = "archived"

    mock_match_id = str(random.randint(100000, 999999))

    mock_game_1_id = str(random.randint(100000, 999999))
    mock_game_2_id = str(random.randint(100000, 999999))
    mock_game_3_id = str(random.randint(100000, 999999))
    mock_game_4_id = str(random.randint(100000, 999999))
    mock_game_5_id = str(random.randint(100000, 999999))

    mocked_player_1_id = str(random.randint(100000, 999999))
    mocked_player_2_id = str(random.randint(100000, 999999))
    mocked_player_3_id = str(random.randint(100000, 999999))
    mocked_player_4_id = str(random.randint(100000, 999999))
    mocked_player_5_id = str(random.randint(100000, 999999))

    def create_mock_game(self):
        mock_game_attrs = {
        "id": int(self.mock_game_2_id),
        "start_time": "2023-08-07T05:00:00Z",
        "block_name": "Playoffs - Round 1",
        "strategy_type": "bestOf",
        "strategy_count": 5,
        "state": "inProgress",
        "number": 2,
        "tournament_id": int(self.mock_tournament_id),
        "team_1_id": int(self.mock_team_1_id),
        "team_2_id": int(self.mock_team_2_id),
        }
        mock_game = Game(**mock_game_attrs)
        return mock_game

    def create_mock_live_game_response(self):
        response = {
            "data": {
                "schedule": {
                    "events": [
                        {
                            "id": self.mock_league_id,
                            "startTime": "2023-08-07T05:00:00Z",
                            "state": "inProgress",
                            "type": "match",
                            "blockName": "Playoffs - Round 1",
                            "league": {
                                "id": self.mock_league_id,
                                "slug": self.mock_league_slug,
                                "name": self.mock_league_name,
                                "image": "http://mock-challengers.png",
                                "priority": 1000,
                                "displayPriority": {
                                    "position": 29,
                                    "status": "not_selected"
                                }
                            },
                            "tournament": {
                                "id": self.mock_tournament_id
                            },
                            "match": {
                                "id": self.mock_match_id,
                                "teams": [
                                    {
                                        "id": self.mock_team_1_id,
                                        "name": self.mock_team_1_name,
                                        "slug": self.mock_team_1_slug,
                                        "code": self.mock_team_1_code,
                                        "image": self.mock_team_1_image,
                                        "result": {
                                            "outcome": None,
                                            "gameWins": 0
                                        },
                                        "record": {
                                            "wins": 0,
                                            "losses": 0
                                        }
                                    },
                                    {
                                        "id": self.mock_team_2_id,
                                        "name": self.mock_team_2_name,
                                        "slug": self.mock_team_2_slug,
                                        "code": self.mock_team_2_code,
                                        "image": self.mock_team_2_image,
                                        "result": {
                                            "outcome": None,
                                            "gameWins": 0
                                        },
                                        "record": {
                                            "wins": 0,
                                            "losses": 0
                                        }
                                    }
                                ],
                                "strategy": {
                                    "type": "bestOf",
                                    "count": 5
                                },
                                "games": [
                                    {
                                        "number": 1,
                                        "id": self.mock_game_1_id,
                                        "state": "completed",
                                        "teams": [
                                            {
                                                "id": self.mock_team_1_id,
                                                "side": "blue"
                                            },
                                            {
                                                "id": self.mock_team_2_id,
                                                "side": "red"
                                            }
                                        ],
                                        "vods": []
                                    },
                                    {
                                        "number": 2,
                                        "id": self.mock_game_2_id,
                                        "state": "inProgress",
                                        "teams": [
                                            {
                                                "id": self.mock_team_1_id,
                                                "side": "blue"
                                            },
                                            {
                                                "id": self.mock_team_2_id,
                                                "side": "red"
                                            }
                                        ],
                                        "vods": []
                                    },
                                    {
                                        "number": 3,
                                        "id": self.mock_game_3_id,
                                        "state": "unstarted",
                                        "teams": [
                                            {
                                                "id": self.mock_team_2_id,
                                                "side": "blue"
                                            },
                                            {
                                                "id": self.mock_team_1_id,
                                                "side": "red"
                                            }
                                        ],
                                        "vods": []
                                    },
                                    {
                                        "number": 4,
                                        "id": self.mock_game_4_id,
                                        "state": "unstarted",
                                        "teams": [
                                            {
                                                "id": self.mock_team_1_id,
                                                "side": "blue"
                                            },
                                            {
                                                "id": self.mock_team_2_id,
                                                "side": "red"
                                            }
                                        ],
                                        "vods": []
                                    },
                                    {
                                        "number": 5,
                                        "id": self.mock_game_5_id,
                                        "state": "unstarted",
                                        "teams": [
                                            {
                                                "id": self.mock_team_2_id,
                                                "side": "blue"
                                            },
                                            {
                                                "id": self.mock_team_1_id,
                                                "side": "red"
                                            }
                                        ],
                                        "vods": []
                                    }
                                ]
                            },
                            "streams": [
                                {
                                    "parameter": "lckcl",
                                    "locale": "ko-KR",
                                    "mediaLocale": {
                                        "locale": "ko-KR",
                                        "englishName": "Korean (Korea)",
                                        "translatedName": "\ud55c\uad6d\uc5b4"
                                    },
                                    "provider": "twitch",
                                    "countries": [],
                                    "offset": -60000,
                                    "statsStatus": "enabled"
                                },
                                {
                                    "parameter": "afchall",
                                    "locale": "ko-KR",
                                    "mediaLocale": {
                                        "locale": "ko-KR",
                                        "englishName": "Korean (Korea)",
                                        "translatedName": "\ud55c\uad6d\uc5b4"
                                    },
                                    "provider": "afreecatv",
                                    "countries": [],
                                    "offset": -60000,
                                    "statsStatus": "enabled"
                                }
                            ]
                        }
                    ]
                }
            }
        }
        return response

    def create_mock_game_state_response(self):
        response = {
            "data": {
                "games": [
                    {
                        "id": self.mock_game_1_id,
                        "state": "completed",
                        "number": 3,
                        "vods": [
                            {
                                "locale": "tr-TR",
                                "mediaLocale": {
                                    "locale": "tr-TR",
                                    "englishName": "Turkish (Turkey)",
                                    "translatedName": "T\u00fcrk\u00e7e"
                                },
                                "parameter": "s8MKRmlG-8s",
                                "provider": "youtube",
                                "offset": 0
                            }
                        ]
                    }
                ]
            }
        }
        return response

    def create_mock_team(self):
        team = ProfessionalTeam(
            int(self.mock_team_1_id),
            self.mock_team_1_slug,
            self.mock_team_1_name,
            self.mock_team_1_code,
            self.mock_team_1_image,
            self.mock_team_1_alt_image,
            self.mock_team_1_background_image,
            self.mock_team_1_status,
            self.mock_league_name
        )
        return team

    def create_mock_team_response(self):
        response = {
            "data": {
                "teams": [
                    {
                        "id": self.mock_team_1_id,
                        "slug": self.mock_team_1_slug,
                        "name": self.mock_team_1_name,
                        "code": self.mock_team_1_code,
                        "image": self.mock_team_1_image,
                        "alternativeImage": self.mock_team_1_alt_image,
                        "backgroundImage": self.mock_team_1_background_image,
                        "status": self.mock_team_1_status,
                        "homeLeague": {
                            "name": self.mock_league_name,
                            "region": self.mock_league_region
                        },
                        "players": [
                            {
                                "id": self.mocked_player_1_id,
                                "summonerName": "MockerPlayer1",
                                "firstName": "mock1first",
                                "lastName": "mock1last",
                                "image": "http://mocked-player-1.png",
                                "role": "top"
                            },
                            {
                                "id": self.mocked_player_2_id,
                                "summonerName": "MockerPlayer2",
                                "firstName": "mock2first",
                                "lastName": "mock2last",
                                "image": "http://mocked-player-1.png",
                                "role": "jungle"
                            },
                            {
                                "id": self.mocked_player_3_id,
                                "summonerName": "MockerPlayer3",
                                "firstName": "mock3first",
                                "lastName": "mock3last",
                                "image": "http://mocked-player-1.png",
                                "role": "mid"
                            },
                            {
                                "id": self.mocked_player_4_id,
                                "summonerName": "MockerPlayer4",
                                "firstName": "mock4first",
                                "lastName": "mock4last",
                                "image": "http://mocked-player-1.png",
                                "role": "bottom"
                            },
                            {
                                "id": self.mocked_player_5_id,
                                "summonerName": "MockerPlayer5",
                                "firstName": "mock5first",
                                "lastName": "mock5last",
                                "image": "http://mocked-player-1.png",
                                "role": "support"
                            },
                        ]
                    }
                ]
            }
        }
        return response

    def create_mock_league(self) -> League:
        league = League(
            int(self.mock_league_id),
            self.mock_league_slug,
            self.mock_league_name,
            self.mock_league_region,
            self.mock_league_image,
            1
        )
        return league

    def create_mock_league_response(self):
        response = {
            "data": {
                "leagues": [
                    {
                        "id": self.mock_league_id,
                        "slug": self.mock_league_slug,
                        "name": self.mock_league_name,
                        "region": self.mock_league_region,
                        "image": self.mock_league_image,
                        "priority": 1,
                        "displayPriority": {
                            "position": 0,
                            "status": "selected"
                        }
                    }
                ]
            }
        }
        return response

    def create_mock_tournament(self):
        tournament = Tournament(
            int(self.mock_tournament_id),
            self.mock_tournament_slug,
            self.mock_tournament_start_date,
            self.mock_tournament_end_date,
            int(self.mock_league_id)
        )
        return tournament

    def create_mock_tournament_response(self):
        response = {
            "data": {
                "leagues": [
                    {
                        "tournaments": [
                            {
                                "id": self.mock_tournament_id,
                                "slug": self.mock_tournament_slug,
                                "startDate": self.mock_tournament_start_date,
                                "endDate": self.mock_tournament_end_date
                            }
                        ]
                    }
                ]
            }
        }
        return response
