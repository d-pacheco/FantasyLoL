import random

from fantasylol.db.models import Game
from fantasylol.db.models import ProfessionalTeam
from fantasylol.db.models import ProfessionalPlayer
from fantasylol.db.models import League
from fantasylol.db.models import Tournament
from fantasylol.db.models import Match


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

    mock_team_1_id = str(random.randint(100000, 999999))
    mock_team_1_name = "Mock Team 1"
    mock_team_1_slug = "mock-team-1"
    mock_team_1_code = "T1"
    mock_team_1_image = "http://mock-team-1-image.png"
    mock_team_1_alt_image = "http://mock-team-1-alternative-image.png"
    mock_team_1_background_image = "http://mock-team-1-background.png"
    mock_team_1_status = "active"

    mock_team_2_id = str(random.randint(100000, 999999))
    mock_team_2_name = "Mock Team 2"
    mock_team_2_slug = "mock-team-2"
    mock_team_2_code = "T2"
    mock_team_2_image = "http://mock-team-2-image.png"
    mock_team_2_alt_image = "http://mock-team-2-alternative-image.png"
    mock_team_2_background_image = "http://mock-team-2-background.png"
    mock_team_2_status = "archived"

    mock_match_id = str(random.randint(100000, 999999))
    mock_match_start_time = "2023-08-07T05:00:00Z"
    mock_block_name = "MockBlock - Round 1"
    mock_match_strategy_type = "bestOf"
    mock_match_strategy_count = 3

    mock_game_1_id = str(random.randint(100000, 999999))
    mock_game_2_id = str(random.randint(100000, 999999))
    mock_game_3_id = str(random.randint(100000, 999999))
    mock_game_4_id = str(random.randint(100000, 999999))
    mock_game_5_id = str(random.randint(100000, 999999))

    mocked_player_1_id = str(random.randint(100000, 999999))
    mocked_player_1_summoner_name = "MockerPlayer1"
    mocked_player_1_first_name = "mock1first",
    mocked_player_1_last_name = "mock1last",
    mocked_player_1_image = "http://mocked-player-1.png"
    mocked_player_1_role = "top"

    mocked_player_2_id = str(random.randint(100000, 999999))
    mocked_player_3_id = str(random.randint(100000, 999999))
    mocked_player_4_id = str(random.randint(100000, 999999))
    mocked_player_5_id = str(random.randint(100000, 999999))

    def create_mock_game(self):
        mock_game_attrs = {
            "id": int(self.mock_game_2_id),
            "state": "inProgress",
            "number": 2,
            "match_id": int(self.mock_match_id),
        }
        return Game(**mock_game_attrs)

    def create_mock_live_game_response(self):
        response = {
            "data": {
                "schedule": {
                    "events": [
                        {
                            "id": self.mock_match_id,
                            "startTime": self.mock_match_start_time,
                            "state": "inProgress",
                            "type": "match",
                            "blockName": self.mock_block_name,
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
                                    "type": self.mock_match_strategy_type,
                                    "count": self.mock_match_strategy_count
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

    def create_mock_player(self):
        mock_player_attrs = {
            "id": self.mocked_player_1_id,
            "summoner_name": self.mocked_player_1_summoner_name,
            "image": self.mocked_player_1_image,
            "role": self.mocked_player_1_role,
            "team_id": int(self.mock_team_1_id)
        }
        return ProfessionalPlayer(**mock_player_attrs)

    def create_mock_team(self):
        mock_team_attrs = {
            "id": int(self.mock_team_1_id),
            "slug": self.mock_team_1_slug,
            "name": self.mock_team_1_name,
            "code": self.mock_team_1_code,
            "image": self.mock_team_1_image,
            "alternative_image": self.mock_team_1_alt_image,
            "background_image": self.mock_team_1_background_image,
            "status": self.mock_team_1_status,
            "home_league": self.mock_league_name
        }
        return ProfessionalTeam(**mock_team_attrs)

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
                                "summonerName": self.mocked_player_1_summoner_name,
                                "firstName": self.mocked_player_1_first_name,
                                "lastName": self.mocked_player_1_last_name,
                                "image": self.mocked_player_1_image,
                                "role": self.mocked_player_1_role
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
        mock_league_attrs = {
            "id": int(self.mock_league_id),
            "slug": self.mock_league_slug,
            "name": self.mock_league_name,
            "region": self.mock_league_region,
            "image": self.mock_league_image,
            "priority": 1  # Adjust the attribute name if needed
        }
        return League(**mock_league_attrs)

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
        mock_tournament_attrs = {
            "id": int(self.mock_tournament_id),
            "slug": self.mock_tournament_slug,
            "start_date": self.mock_tournament_start_date,
            "end_date": self.mock_tournament_end_date,
            "league_id": int(self.mock_league_id)
        }
        return Tournament(**mock_tournament_attrs)

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

    def create_mock_match(self):
        mock_match_attrs = {
            "id": int(self.mock_match_id),
            "start_time": self.mock_match_start_time,
            "block_name": self.mock_block_name,
            "league_name": self.mock_league_name,
            "strategy_type": self.mock_match_strategy_type,
            "strategy_count": self.mock_match_strategy_count,
            "tournament_id": int(self.mock_tournament_id),
            "team_1_name": self.mock_team_1_name,
            "team_2_name": self.mock_team_2_name
        }
        return Match(**mock_match_attrs)

    def create_mock_match_response(self):
        return {
            "data": {
                "schedule": {
                    "events": [
                        {
                            "startTime": self.mock_match_start_time,
                            "blockName": self.mock_block_name,
                            "league": {
                                "name": self.mock_league_name
                            },
                            "match": {
                                "id": self.mock_match_id,
                                "type": "normal",
                                "teams": [
                                    {
                                        "name": self.mock_team_1_name,
                                        "code": self.mock_team_1_code,
                                        "image": self.mock_team_1_image,
                                        "result": {
                                            "gameWins": 2
                                        }
                                    },
                                    {
                                        "name": self.mock_team_2_name,
                                        "code": self.mock_team_2_code,
                                        "image": self.mock_team_2_image,
                                        "result": {
                                            "gameWins": 0
                                        }
                                    }
                                ],
                                "strategy": {
                                    "type": self.mock_match_strategy_type,
                                    "count": self.mock_match_strategy_count
                                }
                            },
                            "games": [
                                {
                                    "id": self.mock_game_1_id,
                                    "vods": [
                                        {
                                            "parameter": "2j4ZiZpjikY"
                                        }
                                    ]
                                },
                                {
                                    "id": self.mock_game_2_id,
                                    "vods": [
                                        {
                                            "parameter": "NJsEWP60paY"
                                        }
                                    ]
                                },
                                {
                                    "id": self.mock_game_3_id,
                                    "vods": []
                                }
                            ]
                        }
                    ]
                }
            }
        }

    def create_mock_window_response(self):
        return {
            "esportsGameId": self.mock_game_1_id,
            "esportsMatchId": self.mock_match_id,
            "gameMetadata": {
                "patchVersion": "13.19.535.4316",
                "blueTeamMetadata": {
                    "esportsTeamId": self.mock_team_1_id,
                    "participantMetadata": [
                        {
                            "participantId": 1,
                            "esportsPlayerId": "99566404810113891",
                            "summonerName": "WBG TheShy",
                            "championId": "Aatrox",
                            "role": "top"
                        },
                        {
                            "participantId": 2,
                            "esportsPlayerId": "102192147302633932",
                            "summonerName": "WBG Weiwei",
                            "championId": "Maokai",
                            "role": "jungle"
                        },
                        {
                            "participantId": 3,
                            "esportsPlayerId": "98767975914916595",
                            "summonerName": "WBG Xiaohu",
                            "championId": "Jayce",
                            "role": "mid"
                        },
                        {
                            "participantId": 4,
                            "esportsPlayerId": "100205573983550103",
                            "summonerName": "WBG Light",
                            "championId": "Senna",
                            "role": "bottom"
                        },
                        {
                            "participantId": 5,
                            "esportsPlayerId": "99566404817393644",
                            "summonerName": "WBG Crisp",
                            "championId": "TahmKench",
                            "role": "support"
                        }
                    ]
                },
                "redTeamMetadata": {
                    "esportsTeamId": self.mock_team_2_id,
                    "participantMetadata": [
                        {
                            "participantId": 6,
                            "esportsPlayerId": "105320680474347057",
                            "summonerName": "T1 Zeus",
                            "championId": "Yone",
                            "role": "top"
                        },
                        {
                            "participantId": 7,
                            "esportsPlayerId": "105320682452092471",
                            "summonerName": "T1 Oner",
                            "championId": "LeeSin",
                            "role": "jungle"
                        },
                        {
                            "participantId": 8,
                            "esportsPlayerId": "98767991747728851",
                            "summonerName": "T1 Faker",
                            "championId": "Ahri",
                            "role": "mid"
                        },
                        {
                            "participantId": 9,
                            "esportsPlayerId": "103495716775975785",
                            "summonerName": "T1 Gumayusi",
                            "championId": "Kalista",
                            "role": "bottom"
                        },
                        {
                            "participantId": 10,
                            "esportsPlayerId": "103495716561790834",
                            "summonerName": "T1 Keria",
                            "championId": "Renata",
                            "role": "support"
                        }
                    ]
                }
            },
            "frames": [{}]
        }
