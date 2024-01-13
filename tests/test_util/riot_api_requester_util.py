from tests.test_util import test_fixtures

get_leagues_mock_response = {
    "data": {
        "leagues": [
            {
                "id": str(test_fixtures.league_fixture.id),
                "slug": test_fixtures.league_fixture.slug,
                "name": test_fixtures.league_fixture.name,
                "region": test_fixtures.league_fixture.region,
                "image": test_fixtures.league_fixture.image,
                "priority": test_fixtures.league_fixture.priority,
                "displayPriority": {
                    "position": 0,
                    "status": "selected"
                }
            }
        ]
    }
}

get_tournaments_for_league_response ={
    "data": {
        "leagues": [
            {
                "tournaments": [
                    {
                        "id": str(test_fixtures.tournament_fixture.id),
                        "slug": test_fixtures.tournament_fixture.slug,
                        "startDate": test_fixtures.tournament_fixture.start_date,
                        "endDate": test_fixtures.tournament_fixture.end_date
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
                "id": str(test_fixtures.team_1_fixture.id),
                "slug": test_fixtures.team_1_fixture.slug,
                "name": test_fixtures.team_1_fixture.name,
                "code": test_fixtures.team_1_fixture.code,
                "image": test_fixtures.team_1_fixture.image,
                "alternativeImage": test_fixtures.team_1_fixture.alternative_image,
                "backgroundImage": test_fixtures.team_1_fixture.background_image,
                "status": test_fixtures.team_1_fixture.status,
                "homeLeague": {
                    "name": test_fixtures.league_fixture.name,
                    "region": test_fixtures.league_fixture.region
                },
                "players": [
                    {
                        "id": str(test_fixtures.player_1_fixture.id),
                        "summonerName": test_fixtures.player_1_fixture.summoner_name,
                        "firstName": "player_1_first_name",
                        "lastName": "player_1_last_name",
                        "image": test_fixtures.player_1_fixture.image,
                        "role": test_fixtures.player_1_fixture.role
                    },
                    {
                        "id": str(test_fixtures.player_2_fixture.id),
                        "summonerName": test_fixtures.player_2_fixture.summoner_name,
                        "firstName": "player_2_first_name",
                        "lastName": "player_2_last_name",
                        "image": test_fixtures.player_2_fixture.image,
                        "role": test_fixtures.player_2_fixture.role
                    },
                    {
                        "id": str(test_fixtures.player_3_fixture.id),
                        "summonerName": test_fixtures.player_3_fixture.summoner_name,
                        "firstName": "player_3_first_name",
                        "lastName": "player_3_last_name",
                        "image": test_fixtures.player_3_fixture.image,
                        "role": test_fixtures.player_3_fixture.role
                    },
                    {
                        "id": str(test_fixtures.player_4_fixture.id),
                        "summonerName": test_fixtures.player_4_fixture.summoner_name,
                        "firstName": "player_4_first_name",
                        "lastName": "player_4_last_name",
                        "image": test_fixtures.player_4_fixture.image,
                        "role": test_fixtures.player_4_fixture.role
                    },
                    {
                        "id": str(test_fixtures.player_5_fixture.id),
                        "summonerName": test_fixtures.player_5_fixture.summoner_name,
                        "firstName": "player_5_first_name",
                        "lastName": "player_5_last_name",
                        "image": test_fixtures.player_5_fixture.image,
                        "role": test_fixtures.player_5_fixture.role
                    },
                ]
            }
        ]
    }
}

get_event_details_response = {
    "data": {
        "event": {
            "id": str(test_fixtures.match_fixture.id),
            "type": "match",
            "tournament": {
                "id": str(test_fixtures.tournament_fixture.id)
            },
            "league": {
                "id": str(test_fixtures.league_fixture.id),
                "slug": test_fixtures.league_fixture.slug,
                "image": test_fixtures.league_fixture.image,
                "name": test_fixtures.league_fixture.name
            },
            "match": {
                "strategy": {
                    "count": test_fixtures.match_fixture.strategy_count
                },
                "teams": [
                    {
                        "id": str(test_fixtures.team_1_fixture.id),
                        "name": test_fixtures.team_1_fixture.name,
                        "code": test_fixtures.team_1_fixture.code,
                        "image": test_fixtures.team_1_fixture.image,
                        "result": {
                            "gameWins": 2
                        }
                    },
                    {
                        "id": str(test_fixtures.team_2_fixture.id),
                        "name": test_fixtures.team_2_fixture.name,
                        "code": test_fixtures.team_2_fixture.code,
                        "image": test_fixtures.team_2_fixture.image,
                        "result": {
                            "gameWins": 0
                        }
                    }
                ],
                "games": [
                    {
                        "number": test_fixtures.game_1_fixture_completed.number,
                        "id": str(test_fixtures.game_1_fixture_completed.id),
                        "state": test_fixtures.game_1_fixture_completed.state.value,
                        "teams": [
                            {
                                "id": str(test_fixtures.team_1_fixture.id),
                                "side": "blue"
                            },
                            {
                                "id": str(test_fixtures.team_2_fixture.id),
                                "side": "red"
                            }
                        ],
                        "vods": []
                    },
                    {
                        "number": test_fixtures.game_2_fixture_inprogress.number,
                        "id": str(test_fixtures.game_2_fixture_inprogress.id),
                        "state": test_fixtures.game_2_fixture_inprogress.state.value,
                        "teams": [
                            {
                                "id": str(test_fixtures.team_1_fixture.id),
                                "side": "blue"
                            },
                            {
                                "id": str(test_fixtures.team_2_fixture.id),
                                "side": "red"
                            }
                        ],
                        "vods": []
                    },
                    {
                        "number": test_fixtures.game_3_fixture_unstarted.number,
                        "id": str(test_fixtures.game_3_fixture_unstarted.id),
                        "state": test_fixtures.game_3_fixture_unstarted.state.value,
                        "teams": [
                            {
                                "id": str(test_fixtures.team_2_fixture.id),
                                "side": "blue"
                            },
                            {
                                "id": str(test_fixtures.team_1_fixture.id),
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

get_games_response = {
    "data": {
        "games": [
            {
                "id": str(test_fixtures.game_1_fixture_completed.id),
                "state": test_fixtures.game_1_fixture_completed.state.value,
                "number": test_fixtures.game_1_fixture_completed.number,
                "vods": []
            }
        ]
    }
}
