from tests.test_util import riot_fixtures
from typing import Dict, List, Any

get_leagues_mock_response = {
    "data": {
        "leagues": [
            {
                "id": riot_fixtures.league_1_fixture.id,
                "slug": riot_fixtures.league_1_fixture.slug,
                "name": riot_fixtures.league_1_fixture.name,
                "region": riot_fixtures.league_1_fixture.region,
                "image": riot_fixtures.league_1_fixture.image,
                "priority": riot_fixtures.league_1_fixture.priority,
                "displayPriority": {
                    "position": 0,
                    "status": "selected"
                }
            }
        ]
    }
}

get_tournaments_for_league_response = {
    "data": {
        "leagues": [
            {
                "tournaments": [
                    {
                        "id": riot_fixtures.tournament_fixture.id,
                        "slug": riot_fixtures.tournament_fixture.slug,
                        "startDate": riot_fixtures.tournament_fixture.start_date,
                        "endDate": riot_fixtures.tournament_fixture.end_date
                    }
                ]
            }
        ]
    }
}

get_teams_response = {
    "data": {
        "teams": [
            {
                "id": riot_fixtures.team_1_fixture.id,
                "slug": riot_fixtures.team_1_fixture.slug,
                "name": riot_fixtures.team_1_fixture.name,
                "code": riot_fixtures.team_1_fixture.code,
                "image": riot_fixtures.team_1_fixture.image,
                "alternativeImage": riot_fixtures.team_1_fixture.alternative_image,
                "backgroundImage": riot_fixtures.team_1_fixture.background_image,
                "status": riot_fixtures.team_1_fixture.status,
                "homeLeague": {
                    "name": riot_fixtures.league_1_fixture.name,
                    "region": riot_fixtures.league_1_fixture.region
                },
                "players": [
                    {
                        "id": riot_fixtures.player_1_fixture.id,
                        "summonerName": riot_fixtures.player_1_fixture.summoner_name,
                        "firstName": "player_1_first_name",
                        "lastName": "player_1_last_name",
                        "image": riot_fixtures.player_1_fixture.image,
                        "role": riot_fixtures.player_1_fixture.role
                    },
                    {
                        "id": riot_fixtures.player_2_fixture.id,
                        "summonerName": riot_fixtures.player_2_fixture.summoner_name,
                        "firstName": "player_2_first_name",
                        "lastName": "player_2_last_name",
                        "image": riot_fixtures.player_2_fixture.image,
                        "role": riot_fixtures.player_2_fixture.role
                    },
                    {
                        "id": riot_fixtures.player_3_fixture.id,
                        "summonerName": riot_fixtures.player_3_fixture.summoner_name,
                        "firstName": "player_3_first_name",
                        "lastName": "player_3_last_name",
                        "image": riot_fixtures.player_3_fixture.image,
                        "role": riot_fixtures.player_3_fixture.role
                    },
                    {
                        "id": riot_fixtures.player_4_fixture.id,
                        "summonerName": riot_fixtures.player_4_fixture.summoner_name,
                        "firstName": "player_4_first_name",
                        "lastName": "player_4_last_name",
                        "image": riot_fixtures.player_4_fixture.image,
                        "role": riot_fixtures.player_4_fixture.role
                    },
                    {
                        "id": riot_fixtures.player_5_fixture.id,
                        "summonerName": riot_fixtures.player_5_fixture.summoner_name,
                        "firstName": "player_5_first_name",
                        "lastName": "player_5_last_name",
                        "image": riot_fixtures.player_5_fixture.image,
                        "role": riot_fixtures.player_5_fixture.role
                    },
                ]
            }
        ]
    }
}

get_event_details_response = {
    "data": {
        "event": {
            "id": riot_fixtures.match_fixture.id,
            "type": "match",
            "tournament": {
                "id": riot_fixtures.tournament_fixture.id
            },
            "league": {
                "id": riot_fixtures.league_1_fixture.id,
                "slug": riot_fixtures.league_1_fixture.slug,
                "image": riot_fixtures.league_1_fixture.image,
                "name": riot_fixtures.league_1_fixture.name
            },
            "match": {
                "strategy": {
                    "count": riot_fixtures.match_fixture.strategy_count
                },
                "teams": [
                    {
                        "id": riot_fixtures.team_1_fixture.id,
                        "name": riot_fixtures.team_1_fixture.name,
                        "code": riot_fixtures.team_1_fixture.code,
                        "image": riot_fixtures.team_1_fixture.image,
                        "result": {
                            "gameWins": 2
                        }
                    },
                    {
                        "id": riot_fixtures.team_2_fixture.id,
                        "name": riot_fixtures.team_2_fixture.name,
                        "code": riot_fixtures.team_2_fixture.code,
                        "image": riot_fixtures.team_2_fixture.image,
                        "result": {
                            "gameWins": 0
                        }
                    }
                ],
                "games": [
                    {
                        "number": riot_fixtures.game_1_fixture_completed.number,
                        "id": riot_fixtures.game_1_fixture_completed.id,
                        "state": riot_fixtures.game_1_fixture_completed.state.value,
                        "teams": [
                            {
                                "id": riot_fixtures.team_1_fixture.id,
                                "side": "blue"
                            },
                            {
                                "id": riot_fixtures.team_2_fixture.id,
                                "side": "red"
                            }
                        ],
                        "vods": []
                    },
                    {
                        "number": riot_fixtures.game_2_fixture_inprogress.number,
                        "id": riot_fixtures.game_2_fixture_inprogress.id,
                        "state": riot_fixtures.game_2_fixture_inprogress.state.value,
                        "teams": [
                            {
                                "id": riot_fixtures.team_1_fixture.id,
                                "side": "blue"
                            },
                            {
                                "id": riot_fixtures.team_2_fixture.id,
                                "side": "red"
                            }
                        ],
                        "vods": []
                    },
                    {
                        "number": riot_fixtures.game_3_fixture_unstarted.number,
                        "id": riot_fixtures.game_3_fixture_unstarted.id,
                        "state": riot_fixtures.game_3_fixture_unstarted.state.value,
                        "teams": [
                            {
                                "id": riot_fixtures.team_2_fixture.id,
                                "side": "blue"
                            },
                            {
                                "id": riot_fixtures.team_1_fixture.id,
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

get_games_response: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
    "data": {
        "games": [
            {
                "id": riot_fixtures.game_1_fixture_completed.id,
                "state": riot_fixtures.game_1_fixture_completed.state.value,
                "number": riot_fixtures.game_1_fixture_completed.number,
                "vods": []
            }
        ]
    }
}

get_livestats_window_response = {
    "esportsGameId": riot_fixtures.game_1_fixture_completed.id,
    "esportsMatchId": riot_fixtures.match_fixture.id,
    "gameMetadata": {
        "patchVersion": "11.2.353.8505",
        "blueTeamMetadata": {
            "esportsTeamId": riot_fixtures.team_1_fixture.id,
            "participantMetadata": [
                {
                    "participantId": riot_fixtures.player_1_game_metadata_fixture.participant_id,
                    "esportsPlayerId": riot_fixtures.player_1_game_metadata_fixture.player_id,
                    "summonerName": f"{riot_fixtures.team_1_fixture.code} "
                    f"{riot_fixtures.player_1_fixture.summoner_name}",
                    "championId": riot_fixtures.player_1_game_metadata_fixture.champion_id,
                    "role": riot_fixtures.player_1_game_metadata_fixture.role
                },
                {
                    "participantId": riot_fixtures.player_2_game_metadata_fixture.participant_id,
                    "esportsPlayerId": riot_fixtures.player_2_game_metadata_fixture.player_id,
                    "summonerName": f"{riot_fixtures.team_1_fixture.code} "
                    f"{riot_fixtures.player_2_fixture.summoner_name}",
                    "championId": riot_fixtures.player_2_game_metadata_fixture.champion_id,
                    "role": riot_fixtures.player_2_game_metadata_fixture.role
                },
                {
                    "participantId": riot_fixtures.player_3_game_metadata_fixture.participant_id,
                    "esportsPlayerId": riot_fixtures.player_3_game_metadata_fixture.player_id,
                    "summonerName": f"{riot_fixtures.team_1_fixture.code} "
                    f"{riot_fixtures.player_3_fixture.summoner_name}",
                    "championId": riot_fixtures.player_3_game_metadata_fixture.champion_id,
                    "role": riot_fixtures.player_3_game_metadata_fixture.role
                },
                {
                    "participantId": riot_fixtures.player_4_game_metadata_fixture.participant_id,
                    "esportsPlayerId": riot_fixtures.player_4_game_metadata_fixture.player_id,
                    "summonerName": f"{riot_fixtures.team_1_fixture.code} "
                    f"{riot_fixtures.player_4_fixture.summoner_name}",
                    "championId": riot_fixtures.player_4_game_metadata_fixture.champion_id,
                    "role": riot_fixtures.player_4_game_metadata_fixture.role
                },
                {
                    "participantId": riot_fixtures.player_5_game_metadata_fixture.participant_id,
                    "esportsPlayerId": riot_fixtures.player_5_game_metadata_fixture.player_id,
                    "summonerName": f"{riot_fixtures.team_1_fixture.code} "
                    f"{riot_fixtures.player_5_fixture.summoner_name}",
                    "championId": riot_fixtures.player_5_game_metadata_fixture.champion_id,
                    "role": riot_fixtures.player_5_game_metadata_fixture.role
                }
            ]
        },
        "redTeamMetadata": {
            "esportsTeamId": riot_fixtures.team_2_fixture.id,
            "participantMetadata": [
                {
                    "participantId": riot_fixtures.player_6_game_metadata_fixture.participant_id,
                    "esportsPlayerId": riot_fixtures.player_6_game_metadata_fixture.player_id,
                    "summonerName": f"{riot_fixtures.team_2_fixture.code} "
                    f"{riot_fixtures.player_6_fixture.summoner_name}",
                    "championId": riot_fixtures.player_6_game_metadata_fixture.champion_id,
                    "role": riot_fixtures.player_6_game_metadata_fixture.role
                },
                {
                    "participantId": riot_fixtures.player_7_game_metadata_fixture.participant_id,
                    "esportsPlayerId": riot_fixtures.player_7_game_metadata_fixture.player_id,
                    "summonerName": f"{riot_fixtures.team_2_fixture.code} "
                    f"{riot_fixtures.player_7_fixture.summoner_name}",
                    "championId": riot_fixtures.player_7_game_metadata_fixture.champion_id,
                    "role": riot_fixtures.player_7_game_metadata_fixture.role
                },
                {
                    "participantId": riot_fixtures.player_8_game_metadata_fixture.participant_id,
                    "esportsPlayerId": riot_fixtures.player_8_game_metadata_fixture.player_id,
                    "summonerName": f"{riot_fixtures.team_2_fixture.code} "
                    f"{riot_fixtures.player_8_fixture.summoner_name}",
                    "championId": riot_fixtures.player_8_game_metadata_fixture.champion_id,
                    "role": riot_fixtures.player_8_game_metadata_fixture.role
                },
                {
                    "participantId": riot_fixtures.player_9_game_metadata_fixture.participant_id,
                    "esportsPlayerId": riot_fixtures.player_9_game_metadata_fixture.player_id,
                    "summonerName": f"{riot_fixtures.team_2_fixture.code} "
                    f"{riot_fixtures.player_9_fixture.summoner_name}",
                    "championId": riot_fixtures.player_9_game_metadata_fixture.champion_id,
                    "role": riot_fixtures.player_9_game_metadata_fixture.role
                },
                {
                    "participantId": riot_fixtures.player_10_game_metadata_fixture.participant_id,
                    "esportsPlayerId": riot_fixtures.player_10_game_metadata_fixture.player_id,
                    "summonerName": f"{riot_fixtures.team_2_fixture.code} "
                    f"{riot_fixtures.player_10_fixture.summoner_name}",
                    "championId": riot_fixtures.player_10_game_metadata_fixture.champion_id,
                    "role": riot_fixtures.player_10_game_metadata_fixture.role
                },
            ]
        }
    },
    "frames": []
}


def percentage_to_float(percentage_value: int) -> float:
    float_value = percentage_value / 100.0
    return float_value


get_live_stats_details_response = {
    "frames": [
        {
            "rfc460Timestamp": "randomTimeStamp",
            "participants": [
                {
                    "participantId": riot_fixtures.player_1_game_stats_fixture.participant_id,
                    "level": 17,
                    "kills": riot_fixtures.player_1_game_stats_fixture.kills,
                    "deaths": riot_fixtures.player_1_game_stats_fixture.deaths,
                    "assists": riot_fixtures.player_1_game_stats_fixture.assists,
                    "totalGoldEarned": riot_fixtures.player_1_game_stats_fixture.total_gold,
                    "creepScore": riot_fixtures.player_1_game_stats_fixture.creep_score,
                    "killParticipation": percentage_to_float(
                        riot_fixtures.player_1_game_stats_fixture.kill_participation),
                    "championDamageShare": percentage_to_float(
                        riot_fixtures.player_1_game_stats_fixture.champion_damage_share),
                    "wardsPlaced": riot_fixtures.player_1_game_stats_fixture.wards_placed,
                    "wardsDestroyed": riot_fixtures.player_1_game_stats_fixture.wards_destroyed,
                    "attackDamage": 250,
                    "abilityPower": 0,
                    "criticalChance": 0.0,
                    "attackSpeed": 139,
                    "lifeSteal": 0,
                    "armor": 115,
                    "magicResistance": 91,
                    "tenacity": 0.0,
                    "items": [
                        3340,
                        3053,
                        6630,
                        3047,
                        3065,
                        2055,
                        2055
                    ],
                    "perkMetadata": {
                        "styleId": 8000,
                        "subStyleId": 8400,
                        "perks": [
                            8010,
                            9111,
                            9105,
                            8299,
                            8444,
                            8453,
                            5008,
                            5008,
                            5002
                        ]
                    },
                    "abilities": [
                        "Q",
                        "E",
                        "W",
                        "Q",
                        "Q",
                        "R",
                        "Q",
                        "E",
                        "Q",
                        "E",
                        "R",
                        "E",
                        "E",
                        "W",
                        "W",
                        "R",
                        "W"
                    ]
                },
                {
                    "participantId": riot_fixtures.player_2_game_stats_fixture.participant_id,
                    "level": 17,
                    "kills": riot_fixtures.player_2_game_stats_fixture.kills,
                    "deaths": riot_fixtures.player_2_game_stats_fixture.deaths,
                    "assists": riot_fixtures.player_2_game_stats_fixture.assists,
                    "totalGoldEarned": riot_fixtures.player_2_game_stats_fixture.total_gold,
                    "creepScore": riot_fixtures.player_2_game_stats_fixture.creep_score,
                    "killParticipation": percentage_to_float(
                        riot_fixtures.player_2_game_stats_fixture.kill_participation
                    ),
                    "championDamageShare": percentage_to_float(
                        riot_fixtures.player_2_game_stats_fixture.champion_damage_share
                    ),
                    "wardsPlaced": riot_fixtures.player_2_game_stats_fixture.wards_placed,
                    "wardsDestroyed": riot_fixtures.player_2_game_stats_fixture.wards_destroyed,
                    "attackDamage": 150,
                    "abilityPower": 0,
                    "criticalChance": 0.0,
                    "attackSpeed": 151,
                    "lifeSteal": 0,
                    "armor": 257,
                    "magicResistance": 166,
                    "tenacity": 0.0,
                    "items": [
                        4401,
                        3105,
                        3047,
                        3143,
                        2055,
                        6664
                    ],
                    "perkMetadata": {
                        "styleId": 8200,
                        "subStyleId": 8000,
                        "perks": [
                            8230,
                            8275,
                            8234,
                            8232,
                            9111,
                            9105,
                            5005,
                            5008,
                            5002
                        ]
                    },
                    "abilities": [
                        "Q",
                        "R",
                        "R",
                        "E",
                        "R",
                        "W",
                        "R",
                        "W",
                        "R",
                        "W",
                        "W",
                        "W",
                        "E",
                        "E",
                        "E",
                        "R",
                        "W"
                    ]
                },
                {
                    "participantId": riot_fixtures.player_3_game_stats_fixture.participant_id,
                    "level": 18,
                    "kills": riot_fixtures.player_3_game_stats_fixture.kills,
                    "deaths": riot_fixtures.player_3_game_stats_fixture.deaths,
                    "assists": riot_fixtures.player_3_game_stats_fixture.assists,
                    "totalGoldEarned": riot_fixtures.player_3_game_stats_fixture.total_gold,
                    "creepScore": riot_fixtures.player_3_game_stats_fixture.creep_score,
                    "killParticipation": percentage_to_float(
                        riot_fixtures.player_3_game_stats_fixture.kill_participation
                    ),
                    "championDamageShare": percentage_to_float(
                        riot_fixtures.player_3_game_stats_fixture.champion_damage_share
                    ),
                    "wardsPlaced": riot_fixtures.player_3_game_stats_fixture.wards_placed,
                    "wardsDestroyed": riot_fixtures.player_3_game_stats_fixture.wards_destroyed,
                    "attackDamage": 84,
                    "abilityPower": 697,
                    "criticalChance": 0.0,
                    "attackSpeed": 169,
                    "lifeSteal": 0,
                    "armor": 68,
                    "magicResistance": 42,
                    "tenacity": 0.0,
                    "items": [
                        3041,
                        3363,
                        3158,
                        2139,
                        6653,
                        3089
                    ],
                    "perkMetadata": {
                        "styleId": 8200,
                        "subStyleId": 8300,
                        "perks": [
                            8230,
                            8226,
                            8210,
                            8237,
                            8345,
                            8352,
                            5005,
                            5008,
                            5003
                        ]
                    },
                    "abilities": [
                        "Q",
                        "W",
                        "E",
                        "Q",
                        "Q",
                        "R",
                        "Q",
                        "W",
                        "Q",
                        "W",
                        "R",
                        "W",
                        "W",
                        "E",
                        "E",
                        "R",
                        "E",
                        "E"
                    ]
                },
                {
                    "participantId": riot_fixtures.player_4_game_stats_fixture.participant_id,
                    "level": 17,
                    "kills": riot_fixtures.player_4_game_stats_fixture.kills,
                    "deaths": riot_fixtures.player_4_game_stats_fixture.deaths,
                    "assists": riot_fixtures.player_4_game_stats_fixture.assists,
                    "totalGoldEarned": riot_fixtures.player_4_game_stats_fixture.total_gold,
                    "creepScore": riot_fixtures.player_4_game_stats_fixture.creep_score,
                    "killParticipation": percentage_to_float(
                        riot_fixtures.player_4_game_stats_fixture.kill_participation
                    ),
                    "championDamageShare": percentage_to_float(
                        riot_fixtures.player_4_game_stats_fixture.champion_damage_share
                    ),
                    "wardsPlaced": riot_fixtures.player_4_game_stats_fixture.wards_placed,
                    "wardsDestroyed": riot_fixtures.player_4_game_stats_fixture.wards_destroyed,
                    "attackDamage": 296,
                    "abilityPower": 0,
                    "criticalChance": 0.0,
                    "attackSpeed": 236,
                    "lifeSteal": 9,
                    "armor": 77,
                    "magicResistance": 37,
                    "tenacity": 0.0,
                    "items": [
                        3363,
                        6676,
                        3046,
                        3006,
                        6671,
                        3031
                    ],
                    "perkMetadata": {
                        "styleId": 8100,
                        "subStyleId": 8000,
                        "perks": [
                            9923,
                            8139,
                            8138,
                            8135,
                            9103,
                            8009,
                            5005,
                            5008,
                            5002
                        ]
                    },
                    "abilities": [
                        "Q",
                        "W",
                        "E",
                        "Q",
                        "Q",
                        "R",
                        "Q",
                        "E",
                        "Q",
                        "E",
                        "R",
                        "Q",
                        "E",
                        "E",
                        "E",
                        "W",
                        "W",
                        "R"
                    ]
                },
                {
                    "participantId": riot_fixtures.player_5_game_stats_fixture.participant_id,
                    "level": 17,
                    "kills": riot_fixtures.player_5_game_stats_fixture.kills,
                    "deaths": riot_fixtures.player_5_game_stats_fixture.deaths,
                    "assists": riot_fixtures.player_5_game_stats_fixture.assists,
                    "totalGoldEarned": riot_fixtures.player_5_game_stats_fixture.total_gold,
                    "creepScore": riot_fixtures.player_5_game_stats_fixture.creep_score,
                    "killParticipation": percentage_to_float(
                        riot_fixtures.player_5_game_stats_fixture.kill_participation
                    ),
                    "championDamageShare": percentage_to_float(
                        riot_fixtures.player_5_game_stats_fixture.champion_damage_share
                    ),
                    "wardsPlaced": riot_fixtures.player_5_game_stats_fixture.wards_placed,
                    "wardsDestroyed": riot_fixtures.player_5_game_stats_fixture.wards_destroyed,
                    "attackDamage": 103,
                    "abilityPower": 20,
                    "criticalChance": 0.0,
                    "attackSpeed": 133,
                    "lifeSteal": 0,
                    "armor": 138,
                    "magicResistance": 83,
                    "tenacity": 0.0,
                    "items": [
                        3364,
                        3190,
                        3067,
                        3117,
                        3024
                    ],
                    "perkMetadata": {
                        "styleId": 8400,
                        "subStyleId": 8300,
                        "perks": [
                            8439,
                            8446,
                            8473,
                            8242,
                            8306,
                            8316,
                            5005,
                            5003,
                            5002
                        ]
                    },
                    "abilities": [
                        "Q",
                        "W",
                        "E",
                        "Q",
                        "Q",
                        "R",
                        "Q",
                        "W",
                        "Q",
                        "W",
                        "R",
                        "W",
                        "W"
                    ]
                },
                {
                    "participantId": riot_fixtures.player_6_game_stats_fixture.participant_id,
                    "level": 17,
                    "kills": riot_fixtures.player_6_game_stats_fixture.kills,
                    "deaths": riot_fixtures.player_6_game_stats_fixture.deaths,
                    "assists": riot_fixtures.player_6_game_stats_fixture.assists,
                    "totalGoldEarned": riot_fixtures.player_6_game_stats_fixture.total_gold,
                    "creepScore": riot_fixtures.player_6_game_stats_fixture.creep_score,
                    "killParticipation": percentage_to_float(
                        riot_fixtures.player_6_game_stats_fixture.kill_participation
                    ),
                    "championDamageShare": percentage_to_float(
                        riot_fixtures.player_6_game_stats_fixture.champion_damage_share
                    ),
                    "wardsPlaced": riot_fixtures.player_6_game_stats_fixture.wards_placed,
                    "wardsDestroyed": riot_fixtures.player_6_game_stats_fixture.wards_destroyed,
                    "attackDamage": 340,
                    "abilityPower": 0,
                    "criticalChance": 0.0,
                    "attackSpeed": 165,
                    "lifeSteal": 12,
                    "armor": 123,
                    "magicResistance": 63,
                    "tenacity": 0.0,
                    "items": [
                        6673,
                        3123,
                        3508,
                        3047,
                        6675
                    ],
                    "perkMetadata": {
                        "styleId": 8400,
                        "subStyleId": 8300,
                        "perks": [
                            8437,
                            8446,
                            8429,
                            8242,
                            8345,
                            8352,
                            5008,
                            5008,
                            5002
                        ]
                    },
                    "abilities": [
                        "Q",
                        "E",
                        "Q",
                        "W",
                        "Q",
                        "R",
                        "Q",
                        "E",
                        "Q",
                        "E",
                        "R",
                        "E",
                        "E",
                        "W",
                        "W",
                        "R"
                    ]
                },
                {
                    "participantId": riot_fixtures.player_7_game_stats_fixture.participant_id,
                    "level": 17,
                    "kills": riot_fixtures.player_7_game_stats_fixture.kills,
                    "deaths": riot_fixtures.player_7_game_stats_fixture.deaths,
                    "assists": riot_fixtures.player_7_game_stats_fixture.assists,
                    "totalGoldEarned": riot_fixtures.player_7_game_stats_fixture.total_gold,
                    "creepScore": riot_fixtures.player_7_game_stats_fixture.creep_score,
                    "killParticipation": percentage_to_float(
                        riot_fixtures.player_7_game_stats_fixture.kill_participation
                    ),
                    "championDamageShare": percentage_to_float(
                        riot_fixtures.player_7_game_stats_fixture.champion_damage_share
                    ),
                    "wardsPlaced": riot_fixtures.player_7_game_stats_fixture.wards_placed,
                    "wardsDestroyed": riot_fixtures.player_7_game_stats_fixture.wards_destroyed,
                    "attackDamage": 102,
                    "abilityPower": 242,
                    "criticalChance": 0.0,
                    "attackSpeed": 132,
                    "lifeSteal": 0,
                    "armor": 119,
                    "magicResistance": 41,
                    "tenacity": 0.0,
                    "items": [
                        3364,
                        3157,
                        3158,
                        3916,
                        6653,
                        1026,
                        2055,
                        2055
                    ],
                    "perkMetadata": {
                        "styleId": 8200,
                        "subStyleId": 8100,
                        "perks": [
                            8230,
                            8275,
                            8234,
                            8232,
                            8126,
                            8135,
                            5008,
                            5008,
                            5002
                        ]
                    },
                    "abilities": [
                        "Q",
                        "W",
                        "Q",
                        "E",
                        "Q",
                        "R",
                        "Q",
                        "E",
                        "Q",
                        "E",
                        "R",
                        "E",
                        "E",
                        "W"
                    ]
                },
                {
                    "participantId": riot_fixtures.player_8_game_stats_fixture.participant_id,
                    "level": 17,
                    "kills": riot_fixtures.player_8_game_stats_fixture.kills,
                    "deaths": riot_fixtures.player_8_game_stats_fixture.deaths,
                    "assists": riot_fixtures.player_8_game_stats_fixture.assists,
                    "totalGoldEarned": riot_fixtures.player_8_game_stats_fixture.total_gold,
                    "creepScore": riot_fixtures.player_8_game_stats_fixture.creep_score,
                    "killParticipation": percentage_to_float(
                        riot_fixtures.player_8_game_stats_fixture.kill_participation
                    ),
                    "championDamageShare": percentage_to_float(
                        riot_fixtures.player_8_game_stats_fixture.champion_damage_share
                    ),
                    "wardsPlaced": riot_fixtures.player_8_game_stats_fixture.wards_placed,
                    "wardsDestroyed": riot_fixtures.player_8_game_stats_fixture.wards_destroyed,
                    "attackDamage": 109,
                    "abilityPower": 376,
                    "criticalChance": 0.0,
                    "attackSpeed": 151,
                    "lifeSteal": 0,
                    "armor": 79,
                    "magicResistance": 59,
                    "tenacity": 0.0,
                    "items": [
                        1058,
                        1058,
                        3363,
                        3020,
                        3100,
                        3152
                    ],
                    "perkMetadata": {
                        "styleId": 8100,
                        "subStyleId": 8200,
                        "perks": [
                            8112,
                            8143,
                            8138,
                            8135,
                            8236,
                            8275,
                            5008,
                            5008,
                            5003
                        ]
                    },
                    "abilities": [
                        "Q",
                        "E",
                        "W",
                        "Q",
                        "Q",
                        "R",
                        "Q",
                        "E",
                        "Q",
                        "E",
                        "R",
                        "E",
                        "E",
                        "W",
                        "W",
                        "R",
                        "W"
                    ]
                },
                {
                    "participantId": riot_fixtures.player_9_game_stats_fixture.participant_id,
                    "level": 17,
                    "kills": riot_fixtures.player_9_game_stats_fixture.kills,
                    "deaths": riot_fixtures.player_9_game_stats_fixture.deaths,
                    "assists": riot_fixtures.player_9_game_stats_fixture.assists,
                    "totalGoldEarned": riot_fixtures.player_9_game_stats_fixture.total_gold,
                    "creepScore": riot_fixtures.player_9_game_stats_fixture.creep_score,
                    "killParticipation": percentage_to_float(
                        riot_fixtures.player_9_game_stats_fixture.kill_participation
                    ),
                    "championDamageShare": percentage_to_float(
                        riot_fixtures.player_9_game_stats_fixture.champion_damage_share
                    ),
                    "wardsPlaced": riot_fixtures.player_9_game_stats_fixture.wards_placed,
                    "wardsDestroyed": riot_fixtures.player_9_game_stats_fixture.wards_destroyed,
                    "attackDamage": 568,
                    "abilityPower": 0,
                    "criticalChance": 0.0,
                    "attackSpeed": 120,
                    "lifeSteal": 9,
                    "armor": 92,
                    "magicResistance": 36,
                    "tenacity": 0.0,
                    "items": [
                        3363,
                        3123,
                        6676,
                        3047,
                        3031,
                        1036,
                        6671,
                        2140
                    ],
                    "perkMetadata": {
                        "styleId": 8000,
                        "subStyleId": 8200,
                        "perks": [
                            8021,
                            8009,
                            9103,
                            8017,
                            8275,
                            8234,
                            5008,
                            5008,
                            5002
                        ]
                    },
                    "abilities": [
                        "Q",
                        "W",
                        "Q",
                        "W",
                        "Q",
                        "R",
                        "Q",
                        "W",
                        "Q",
                        "W",
                        "R",
                        "W",
                        "E",
                        "E"
                    ]
                },
                {
                    "participantId": riot_fixtures.player_10_game_stats_fixture.participant_id,
                    "level": 17,
                    "kills": riot_fixtures.player_10_game_stats_fixture.kills,
                    "deaths": riot_fixtures.player_10_game_stats_fixture.deaths,
                    "assists": riot_fixtures.player_10_game_stats_fixture.assists,
                    "totalGoldEarned": riot_fixtures.player_10_game_stats_fixture.total_gold,
                    "creepScore": riot_fixtures.player_10_game_stats_fixture.creep_score,
                    "killParticipation": percentage_to_float(
                        riot_fixtures.player_10_game_stats_fixture.kill_participation
                    ),
                    "championDamageShare": percentage_to_float(
                        riot_fixtures.player_10_game_stats_fixture.champion_damage_share
                    ),
                    "wardsPlaced": riot_fixtures.player_10_game_stats_fixture.wards_placed,
                    "wardsDestroyed": riot_fixtures.player_10_game_stats_fixture.wards_destroyed,
                    "attackDamage": 93,
                    "abilityPower": 30,
                    "criticalChance": 0.0,
                    "attackSpeed": 128,
                    "lifeSteal": 0,
                    "armor": 118,
                    "magicResistance": 82,
                    "tenacity": 0.0,
                    "items": [
                        3009,
                        3364,
                        1028,
                        3190,
                        2055,
                        2055,
                        3067
                    ],
                    "perkMetadata": {
                        "styleId": 8400,
                        "subStyleId": 8300,
                        "perks": [
                            8439,
                            8463,
                            8473,
                            8242,
                            8306,
                            8316,
                            5008,
                            5002,
                            5003
                        ]
                    },
                    "abilities": [
                        "Q",
                        "E",
                        "W",
                        "W",
                        "W",
                        "R",
                        "W",
                        "Q",
                        "W",
                        "E",
                        "R",
                        "E"
                    ]
                }
            ]
        }
    ]
}

get_live_stats_details_empty_frames_response: Dict[str, list] = {
    "frames": []
}

get_schedule_response = {
    "data": {
        "schedule": {
            "pages": {
                "older": "olderToken",
                "newer": "newerToken"
            },
            "events": [
                {
                    "startTime": riot_fixtures.match_fixture.start_time,
                    "state": "completed",
                    "type": "match",
                    "blockName": riot_fixtures.match_fixture.block_name,
                    "league": {
                        "name": riot_fixtures.league_1_fixture.name,
                        "slug": riot_fixtures.league_1_fixture.slug
                    },
                    "match": {
                        "id": riot_fixtures.match_fixture.id,
                        "flags": [
                            "hasVod",
                            "isSpoiler"
                        ],
                        "teams": [
                            {
                                "name": riot_fixtures.team_1_fixture.name,
                                "code": riot_fixtures.team_1_fixture.code,
                                "image": riot_fixtures.team_1_fixture.image,
                                "result": {
                                    "outcome": "loss",
                                    "gameWins": 1
                                },
                                "record": {
                                    "wins": 1,
                                    "losses": 1
                                }
                            },
                            {
                                "name": riot_fixtures.team_2_fixture.name,
                                "code": riot_fixtures.team_2_fixture.code,
                                "image": riot_fixtures.team_2_fixture.image,
                                "result": {
                                    "outcome": "win",
                                    "gameWins": 2
                                },
                                "record": {
                                    "wins": 3,
                                    "losses": 0
                                }
                            }
                        ],
                        "strategy": {
                            "type": riot_fixtures.match_fixture.strategy_type,
                            "count": riot_fixtures.match_fixture.strategy_count
                        }
                    }
                }
            ]
        }
    }
}
