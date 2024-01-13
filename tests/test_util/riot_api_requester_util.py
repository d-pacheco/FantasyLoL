from tests.test_util.test_fixtures import TestFixtures


class RiotApiRequesterUtil:
    get_leagues_mock_response = {
        "data": {
            "leagues": [
                {
                    "id": str(TestFixtures.league_fixture.id),
                    "slug": TestFixtures.league_fixture.slug,
                    "name": TestFixtures.league_fixture.name,
                    "region": TestFixtures.league_fixture.region,
                    "image": TestFixtures.league_fixture.image,
                    "priority": TestFixtures.league_fixture.priority,
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
                            "id": str(TestFixtures.tournament_fixture.id),
                            "slug": TestFixtures.tournament_fixture.slug,
                            "startDate": TestFixtures.tournament_fixture.start_date,
                            "endDate": TestFixtures.tournament_fixture.end_date
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
                    "id": str(TestFixtures.team_1_fixture.id),
                    "slug": TestFixtures.team_1_fixture.slug,
                    "name": TestFixtures.team_1_fixture.name,
                    "code": TestFixtures.team_1_fixture.code,
                    "image": TestFixtures.team_1_fixture.image,
                    "alternativeImage": TestFixtures.team_1_fixture.alternative_image,
                    "backgroundImage": TestFixtures.team_1_fixture.background_image,
                    "status": TestFixtures.team_1_fixture.status,
                    "homeLeague": {
                        "name": TestFixtures.league_fixture.name,
                        "region": TestFixtures.league_fixture.region
                    },
                    "players": [
                        {
                            "id": str(TestFixtures.player_1_fixture.id),
                            "summonerName": TestFixtures.player_1_fixture.summoner_name,
                            "firstName": "player_1_first_name",
                            "lastName": "player_1_last_name",
                            "image": TestFixtures.player_1_fixture.image,
                            "role": TestFixtures.player_1_fixture.role
                        },
                        {
                            "id": str(TestFixtures.player_2_fixture.id),
                            "summonerName": TestFixtures.player_2_fixture.summoner_name,
                            "firstName": "player_2_first_name",
                            "lastName": "player_2_last_name",
                            "image": TestFixtures.player_2_fixture.image,
                            "role": TestFixtures.player_2_fixture.role
                        },
                        {
                            "id": str(TestFixtures.player_3_fixture.id),
                            "summonerName": TestFixtures.player_3_fixture.summoner_name,
                            "firstName": "player_3_first_name",
                            "lastName": "player_3_last_name",
                            "image": TestFixtures.player_3_fixture.image,
                            "role": TestFixtures.player_3_fixture.role
                        },
                        {
                            "id": str(TestFixtures.player_4_fixture.id),
                            "summonerName": TestFixtures.player_4_fixture.summoner_name,
                            "firstName": "player_4_first_name",
                            "lastName": "player_4_last_name",
                            "image": TestFixtures.player_4_fixture.image,
                            "role": TestFixtures.player_4_fixture.role
                        },
                        {
                            "id": str(TestFixtures.player_5_fixture.id),
                            "summonerName": TestFixtures.player_5_fixture.summoner_name,
                            "firstName": "player_5_first_name",
                            "lastName": "player_5_last_name",
                            "image": TestFixtures.player_5_fixture.image,
                            "role": TestFixtures.player_5_fixture.role
                        },
                    ]
                }
            ]
        }
    }

    get_event_details_response = {
        "data": {
            "event": {
                "id": str(TestFixtures.match_fixture.id),
                "type": "match",
                "tournament": {
                    "id": str(TestFixtures.tournament_fixture.id)
                },
                "league": {
                    "id": str(TestFixtures.league_fixture.id),
                    "slug": TestFixtures.league_fixture.slug,
                    "image": TestFixtures.league_fixture.image,
                    "name": TestFixtures.league_fixture.name
                },
                "match": {
                    "strategy": {
                        "count": TestFixtures.match_fixture.strategy_count
                    },
                    "teams": [
                        {
                            "id": str(TestFixtures.team_1_fixture.id),
                            "name": TestFixtures.team_1_fixture.name,
                            "code": TestFixtures.team_1_fixture.code,
                            "image": TestFixtures.team_1_fixture.image,
                            "result": {
                                "gameWins": 2
                            }
                        },
                        {
                            "id": str(TestFixtures.team_2_fixture.id),
                            "name": TestFixtures.team_2_fixture.name,
                            "code": TestFixtures.team_2_fixture.code,
                            "image": TestFixtures.team_2_fixture.image,
                            "result": {
                                "gameWins": 0
                            }
                        }
                    ],
                    "games": [
                        {
                            "number": TestFixtures.game_1_fixture_completed.number,
                            "id": str(TestFixtures.game_1_fixture_completed.id),
                            "state": TestFixtures.game_1_fixture_completed.state.value,
                            "teams": [
                                {
                                    "id": str(TestFixtures.team_1_fixture.id),
                                    "side": "blue"
                                },
                                {
                                    "id": str(TestFixtures.team_2_fixture.id),
                                    "side": "red"
                                }
                            ],
                            "vods": []
                        },
                        {
                            "number": TestFixtures.game_2_fixture_inprogress.number,
                            "id": str(TestFixtures.game_2_fixture_inprogress.id),
                            "state": TestFixtures.game_2_fixture_inprogress.state.value,
                            "teams": [
                                {
                                    "id": str(TestFixtures.team_1_fixture.id),
                                    "side": "blue"
                                },
                                {
                                    "id": str(TestFixtures.team_2_fixture.id),
                                    "side": "red"
                                }
                            ],
                            "vods": []
                        },
                        {
                            "number": TestFixtures.game_3_fixture_unstarted.number,
                            "id": str(TestFixtures.game_3_fixture_unstarted.id),
                            "state": TestFixtures.game_3_fixture_unstarted.state.value,
                            "teams": [
                                {
                                    "id": str(TestFixtures.team_2_fixture.id),
                                    "side": "blue"
                                },
                                {
                                    "id": str(TestFixtures.team_1_fixture.id),
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
                    "id": str(TestFixtures.game_1_fixture_completed.id),
                    "state": TestFixtures.game_1_fixture_completed.state.value,
                    "number": TestFixtures.game_1_fixture_completed.number,
                    "vods": []
                }
            ]
        }
    }
