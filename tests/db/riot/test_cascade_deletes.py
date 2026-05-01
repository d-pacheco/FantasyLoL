from tests.test_base import TestBase
from tests.test_util import riot_fixtures
from src.common.schemas.riot_data_schemas import TeamGameStats
from src.db.models import LeagueModel, ProfessionalTeamModel, GameModel, MatchModel, EventTeamsModel


class TestCascadeDeletes(TestBase):
    def setUp(self):
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_team(riot_fixtures.team_1_fixture)
        self.db.put_team(riot_fixtures.team_2_fixture)

    def _delete_league(self, league_id):
        with self.db_provider.get_db() as session:
            session.query(LeagueModel).filter(LeagueModel.id == league_id).delete()
            session.commit()

    def _delete_team(self, team_id):
        with self.db_provider.get_db() as session:
            session.query(ProfessionalTeamModel).filter(
                ProfessionalTeamModel.id == team_id
            ).delete()
            session.commit()

    def _delete_game(self, game_id):
        with self.db_provider.get_db() as session:
            session.query(GameModel).filter(GameModel.id == game_id).delete()
            session.commit()

    def test_deleting_league_cascades_to_tournaments(self):
        # Arrange
        tournament = riot_fixtures.tournament_fixture
        self.db.put_tournament(tournament)
        self.assertIsNotNone(self.db.get_tournament_by_id(tournament.id))

        # Act
        self._delete_league(riot_fixtures.league_1_fixture.id)

        # Assert
        self.assertIsNone(self.db.get_tournament_by_id(tournament.id))

    def test_deleting_league_cascades_through_tournaments_to_matches(self):
        # Arrange
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        match = riot_fixtures.match_fixture
        self.db.put_match(match)
        self.assertIsNotNone(self.db.get_match_by_id(match.id))

        # Act
        self._delete_league(riot_fixtures.league_1_fixture.id)

        # Assert
        self.assertIsNone(self.db.get_match_by_id(match.id))

    def test_deleting_league_cascades_through_to_games(self):
        # Arrange
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_match(riot_fixtures.match_fixture)
        game = riot_fixtures.game_1_fixture_completed
        self.db.put_game(game)
        self.assertIsNotNone(self.db.get_game_by_id(game.id))

        # Act
        self._delete_league(riot_fixtures.league_1_fixture.id)

        # Assert
        self.assertIsNone(self.db.get_game_by_id(game.id))

    def test_deleting_league_cascades_through_to_player_game_metadata(self):
        # Arrange
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_match(riot_fixtures.match_fixture)
        self.db.put_game(riot_fixtures.game_1_fixture_completed)
        metadata = riot_fixtures.player_1_game_metadata_fixture
        self.db.put_player_metadata(metadata)
        self.assertIsNotNone(self.db.get_player_metadata(metadata.player_id, metadata.game_id))

        # Act
        self._delete_league(riot_fixtures.league_1_fixture.id)

        # Assert
        self.assertIsNone(self.db.get_player_metadata(metadata.player_id, metadata.game_id))

    def test_deleting_league_cascades_through_to_player_game_stats(self):
        # Arrange
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_match(riot_fixtures.match_fixture)
        self.db.put_game(riot_fixtures.game_1_fixture_completed)
        stats = riot_fixtures.player_1_game_stats_fixture
        self.db.put_player_stats(stats)
        self.assertIsNotNone(self.db.get_player_stats(stats.game_id, stats.participant_id))

        # Act
        self._delete_league(riot_fixtures.league_1_fixture.id)

        # Assert
        self.assertIsNone(self.db.get_player_stats(stats.game_id, stats.participant_id))

    def test_deleting_league_cascades_through_to_team_game_stats(self):
        # Arrange
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_match(riot_fixtures.match_fixture)
        self.db.put_game(riot_fixtures.game_1_fixture_completed)
        team_stats = TeamGameStats(
            game_id=riot_fixtures.game_1_fixture_completed.id,
            team_id=riot_fixtures.team_1_fixture.id,
            total_gold=50000,
            inhibitors=2,
            towers=8,
            barons=1,
            total_kills=20,
        )
        self.db.put_team_stats(team_stats)

        # Act
        self._delete_league(riot_fixtures.league_1_fixture.id)

        # Assert — game is gone, so team_game_stats must be gone too
        self.assertIsNone(self.db.get_game_by_id(riot_fixtures.game_1_fixture_completed.id))

    def test_deleting_team_cascades_to_players(self):
        # Arrange
        player = riot_fixtures.player_1_fixture
        self.db.put_player(player)
        self.assertIsNotNone(self.db.get_player_by_id(player.id))

        # Act
        self._delete_team(riot_fixtures.team_1_fixture.id)

        # Assert
        self.assertIsNone(self.db.get_player_by_id(player.id))

    def test_deleting_game_cascades_to_player_game_metadata(self):
        # Arrange
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_match(riot_fixtures.match_fixture)
        game = riot_fixtures.game_1_fixture_completed
        self.db.put_game(game)
        metadata = riot_fixtures.player_1_game_metadata_fixture
        self.db.put_player_metadata(metadata)
        self.assertIsNotNone(self.db.get_player_metadata(metadata.player_id, metadata.game_id))

        # Act
        self._delete_game(game.id)

        # Assert
        self.assertIsNone(self.db.get_player_metadata(metadata.player_id, metadata.game_id))

    def test_deleting_game_cascades_to_player_game_stats(self):
        # Arrange
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_match(riot_fixtures.match_fixture)
        game = riot_fixtures.game_1_fixture_completed
        self.db.put_game(game)
        stats = riot_fixtures.player_1_game_stats_fixture
        self.db.put_player_stats(stats)
        self.assertIsNotNone(self.db.get_player_stats(stats.game_id, stats.participant_id))

        # Act
        self._delete_game(game.id)

        # Assert
        self.assertIsNone(self.db.get_player_stats(stats.game_id, stats.participant_id))

    def test_deleting_match_cascades_to_event_teams(self):
        # Arrange
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_match(riot_fixtures.match_fixture)
        match_id = riot_fixtures.match_fixture.id

        with self.db_provider.get_db() as session:
            rows = session.query(EventTeamsModel).filter(EventTeamsModel.match_id == match_id).all()
            self.assertTrue(len(rows) > 0)

        # Act
        with self.db_provider.get_db() as session:
            session.query(MatchModel).filter(MatchModel.id == match_id).delete()
            session.commit()

        # Assert
        with self.db_provider.get_db() as session:
            rows = session.query(EventTeamsModel).filter(EventTeamsModel.match_id == match_id).all()
            self.assertEqual(0, len(rows))
