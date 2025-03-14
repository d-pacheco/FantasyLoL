from src.common.schemas.riot_data_schemas import Match, League, ProfessionalTeam, MatchState, \
    ProfessionalPlayer, Game, PlayerGameMetadata, PlayerGameStats
from tests.test_util import riot_fixtures
from typing import Any

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


def create_player_for_team_response(player: ProfessionalPlayer, player_number: int) -> dict:
    return {
        "id": player.id,
        "summonerName": player.summoner_name,
        "firstName": f"player_{player_number}_first_name",
        "lastName": f"player_{player_number}_last_name",
        "image": player.image,
        "role": player.role
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
                    create_player_for_team_response(riot_fixtures.player_1_fixture, 1),
                    create_player_for_team_response(riot_fixtures.player_2_fixture, 2),
                    create_player_for_team_response(riot_fixtures.player_3_fixture, 3),
                    create_player_for_team_response(riot_fixtures.player_4_fixture, 4),
                    create_player_for_team_response(riot_fixtures.player_5_fixture, 5),
                ]
            }
        ]
    }
}


def create_team_for_event_details_response(
        team: ProfessionalTeam,
        match: Match = riot_fixtures.match_fixture
) -> dict:
    game_wins = None
    if team.name == match.team_1_name:
        game_wins = match.team_1_wins
    elif team.name == match.team_2_name:
        game_wins = match.team_2_wins

    assert (game_wins is not None)
    return {
        "id": team.id,
        "name": team.name,
        "code": team.code,
        "image": team.image,
        "result": {
            "gameWins": game_wins
        }
    }


def create_game_for_response(
        game: Game,
        blue_team: ProfessionalTeam | None = None,
        red_team: ProfessionalTeam | None = None
) -> dict:
    game_response = {
        "id": game.id,
        "number": game.number,
        "state": game.state.value,
        "vods": []
    }
    if blue_team and red_team:
        game_response["teams"] = [
            {
                "id": blue_team.id,
                "side": "blue"
            },
            {
                "id": red_team.id,
                "side": "red"
            }
        ]
    return game_response


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
                    create_team_for_event_details_response(riot_fixtures.team_1_fixture),
                    create_team_for_event_details_response(riot_fixtures.team_2_fixture)
                ],
                "games": [
                    create_game_for_response(
                        riot_fixtures.game_1_fixture_completed,
                        riot_fixtures.team_1_fixture,
                        riot_fixtures.team_2_fixture
                    ),
                    create_game_for_response(
                        riot_fixtures.game_2_fixture_inprogress,
                        riot_fixtures.team_1_fixture,
                        riot_fixtures.team_2_fixture
                    ),
                    create_game_for_response(
                        riot_fixtures.game_3_fixture_unstarted,
                        riot_fixtures.team_2_fixture,
                        riot_fixtures.team_1_fixture
                    )
                ]
            },
            "streams": []
        }
    }
}

get_games_response: dict[str, dict[str, list[dict[str, Any]]]] = {
    "data": {
        "games": [
            create_game_for_response(riot_fixtures.game_1_fixture_completed)
        ]
    }
}


def create_participant_metadata_for_response(
        player_game_metadata: PlayerGameMetadata,
        player: ProfessionalPlayer,
        team: ProfessionalTeam,
) -> dict:
    return {
        "participantId": player_game_metadata.participant_id,
        "esportsPlayerId": player_game_metadata.player_id,
        "summonerName": f"{team.code} {player.summoner_name}",
        "championId": player_game_metadata.champion_id,
        "role": player_game_metadata.role
    }


get_livestats_window_response = {
    "esportsGameId": riot_fixtures.game_1_fixture_completed.id,
    "esportsMatchId": riot_fixtures.match_fixture.id,
    "gameMetadata": {
        "patchVersion": "11.2.353.8505",
        "blueTeamMetadata": {
            "esportsTeamId": riot_fixtures.team_1_fixture.id,
            "participantMetadata": [
                create_participant_metadata_for_response(
                    riot_fixtures.player_1_game_metadata_fixture,
                    riot_fixtures.player_1_fixture,
                    riot_fixtures.team_1_fixture
                ),
                create_participant_metadata_for_response(
                    riot_fixtures.player_2_game_metadata_fixture,
                    riot_fixtures.player_2_fixture,
                    riot_fixtures.team_1_fixture
                ),
                create_participant_metadata_for_response(
                    riot_fixtures.player_3_game_metadata_fixture,
                    riot_fixtures.player_3_fixture,
                    riot_fixtures.team_1_fixture
                ),
                create_participant_metadata_for_response(
                    riot_fixtures.player_4_game_metadata_fixture,
                    riot_fixtures.player_4_fixture,
                    riot_fixtures.team_1_fixture
                ),
                create_participant_metadata_for_response(
                    riot_fixtures.player_5_game_metadata_fixture,
                    riot_fixtures.player_5_fixture,
                    riot_fixtures.team_1_fixture
                )
            ]
        },
        "redTeamMetadata": {
            "esportsTeamId": riot_fixtures.team_2_fixture.id,
            "participantMetadata": [
                create_participant_metadata_for_response(
                    riot_fixtures.player_6_game_metadata_fixture,
                    riot_fixtures.player_6_fixture,
                    riot_fixtures.team_2_fixture
                ),
                create_participant_metadata_for_response(
                    riot_fixtures.player_7_game_metadata_fixture,
                    riot_fixtures.player_7_fixture,
                    riot_fixtures.team_2_fixture
                ),
                create_participant_metadata_for_response(
                    riot_fixtures.player_8_game_metadata_fixture,
                    riot_fixtures.player_8_fixture,
                    riot_fixtures.team_2_fixture
                ),
                create_participant_metadata_for_response(
                    riot_fixtures.player_9_game_metadata_fixture,
                    riot_fixtures.player_9_fixture,
                    riot_fixtures.team_2_fixture
                ),
                create_participant_metadata_for_response(
                    riot_fixtures.player_10_game_metadata_fixture,
                    riot_fixtures.player_10_fixture,
                    riot_fixtures.team_2_fixture
                ),
            ]
        }
    },
    "frames": []
}


def percentage_to_float(percentage_value: int) -> float:
    float_value = percentage_value / 100.0
    return float_value


def create_participant_for_response(player_game_stats: PlayerGameStats) -> dict:
    return {
        "participantId": player_game_stats.participant_id,
        "level": 17,
        "kills": player_game_stats.kills,
        "deaths": player_game_stats.deaths,
        "assists": player_game_stats.assists,
        "totalGoldEarned": player_game_stats.total_gold,
        "creepScore": player_game_stats.creep_score,
        "killParticipation": percentage_to_float(player_game_stats.kill_participation),
        "championDamageShare": percentage_to_float(player_game_stats.champion_damage_share),
        "wardsPlaced": player_game_stats.wards_placed,
        "wardsDestroyed": player_game_stats.wards_destroyed,
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
    }


get_live_stats_details_empty_frames_response: dict[str, list] = {
    "frames": []
}

get_live_stats_details_response = {
    "frames": [
        {
            "rfc460Timestamp": "randomTimeStamp",
            "participants": [
                create_participant_for_response(riot_fixtures.player_1_game_stats_fixture),
                create_participant_for_response(riot_fixtures.player_2_game_stats_fixture),
                create_participant_for_response(riot_fixtures.player_3_game_stats_fixture),
                create_participant_for_response(riot_fixtures.player_4_game_stats_fixture),
                create_participant_for_response(riot_fixtures.player_5_game_stats_fixture),
                create_participant_for_response(riot_fixtures.player_6_game_stats_fixture),
                create_participant_for_response(riot_fixtures.player_7_game_stats_fixture),
                create_participant_for_response(riot_fixtures.player_8_game_stats_fixture),
                create_participant_for_response(riot_fixtures.player_9_game_stats_fixture),
                create_participant_for_response(riot_fixtures.player_10_game_stats_fixture)
            ]
        }
    ]
}


def create_get_schedule_response(
        match: Match,
        league: League = riot_fixtures.league_1_fixture,
        team_1: ProfessionalTeam = riot_fixtures.team_1_fixture,
        team_2: ProfessionalTeam = riot_fixtures.team_2_fixture
) -> dict:
    team_1_result = None
    team_2_result = None
    if match.state == MatchState.COMPLETED:
        team_1_result = {
            "outcome": "win" if match.winning_team == team_1.name else "loss",
            "gameWins": match.team_1_wins
        }
        team_2_result = {
            "outcome": "win" if match.winning_team == team_2.name else "loss",
            "gameWins": match.team_2_wins
        }
    elif match.state == MatchState.INPROGRESS:
        team_1_result = {
            "outcome": None,
            "gameWins": match.team_1_wins
        }
        team_2_result = {
            "outcome": None,
            "gameWins": match.team_2_wins
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
                        "startTime": match.start_time,
                        "state": match.state,
                        "type": "match",
                        "blockName": match.block_name,
                        "league": {
                            "name": league.name,
                            "slug": league.slug
                        },
                        "match": {
                            "id": match.id,
                            "flags": [
                                "hasVod",
                                "isSpoiler"
                            ],
                            "teams": [
                                {
                                    "name": team_1.name,
                                    "code": team_1.code,
                                    "image": team_1.image,
                                    "result": team_1_result,
                                    "record": {
                                        "wins": 1,
                                        "losses": 1
                                    }
                                },
                                {
                                    "name": team_2.name,
                                    "code": team_2.code,
                                    "image": team_2.image,
                                    "result": team_2_result,
                                    "record": {
                                        "wins": 3,
                                        "losses": 0
                                    }
                                }
                            ],
                            "strategy": {
                                "type": match.strategy_type,
                                "count": match.strategy_count
                            }
                        }
                    }
                ]
            }
        }
    }

    return get_schedule_response
