from unittest.mock import patch
import uuid

from tests.test_base import FantasyLolTestBase
from tests.test_util import fantasy_fixtures
from tests.test_util import riot_fixtures

from src.common.schemas.fantasy_schemas import (
    FantasyLeagueStatus
)
from src.common.exceptions.league_not_found_exception import LeagueNotFoundException

from src.db.models import (
    FantasyLeagueModel,
    LeagueModel
)

from src.fantasy.exceptions.fantasy_league_not_found_exception import \
    FantasyLeagueNotFoundException
from src.fantasy.exceptions.fantasy_league_invalid_required_state_exception import \
    FantasyLeagueInvalidRequiredStateException
from src.fantasy.exceptions.fantasy_unavailable_exception import FantasyUnavailableException
from src.fantasy.util.fantasy_league_util import FantasyLeagueUtil

fantasy_league_util = FantasyLeagueUtil()

BASE_CRUD_PATH = 'src.db.crud'


class TestFantasyLeagueUtil(FantasyLolTestBase):
    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_by_id')
    def test_validate_league_successful(self, mock_get_fantasy_league_by_id):
        # Arrange
        expected_fantasy_league_model = create_fantasy_league_model(FantasyLeagueStatus.DRAFT, 1)
        mock_get_fantasy_league_by_id.return_value = expected_fantasy_league_model

        # Act
        returned_fantasy_league_model = fantasy_league_util.validate_league(
            expected_fantasy_league_model.id, [FantasyLeagueStatus.DRAFT]
        )

        # Assert
        self.assertEqual(expected_fantasy_league_model, returned_fantasy_league_model)

    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_by_id')
    def test_validate_league_league_not_found_exception(self, mock_get_fantasy_league_by_id):
        # Arrange
        mock_get_fantasy_league_by_id.return_value = None

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            fantasy_league_util.validate_league("someId", [FantasyLeagueStatus.DRAFT])

    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_by_id')
    def test_validate_league_not_in_required_state(self, mock_get_fantasy_league_by_id):
        # Arrange
        expected_fantasy_league_model = create_fantasy_league_model(
            FantasyLeagueStatus.PRE_DRAFT, 1
        )
        mock_get_fantasy_league_by_id.return_value = expected_fantasy_league_model

        # Act and Assert
        with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
            fantasy_league_util.validate_league(
                expected_fantasy_league_model.id, [FantasyLeagueStatus.DRAFT]
            )

    @patch(f'{BASE_CRUD_PATH}.get_fantasy_league_by_id')
    def test_validate_league_no_required_state_should_return_fantasy_league_if_it_exists(
            self, mock_get_fantasy_league_by_id):
        # Arrange
        expected_fantasy_league_model = create_fantasy_league_model(FantasyLeagueStatus.DRAFT, 1)
        mock_get_fantasy_league_by_id.return_value = expected_fantasy_league_model

        # Act
        returned_fantasy_league_model = fantasy_league_util.validate_league(
            expected_fantasy_league_model.id
        )

        # Assert
        self.assertEqual(expected_fantasy_league_model, returned_fantasy_league_model)

    @patch(f'{BASE_CRUD_PATH}.get_leagues')
    def test_validate_available_leagues_successful(self, mock_get_leagues):
        # Arrange
        riot_leagues = [
            LeagueModel(**riot_fixtures.league_1_fixture.model_dump()),
            LeagueModel(**riot_fixtures.league_2_fixture.model_dump())
        ]
        mock_get_leagues.return_value = riot_leagues
        selected_league_ids = [riot_fixtures.league_2_fixture.id]

        # Act and Assert
        try:
            fantasy_league_util.validate_available_leagues(selected_league_ids)
        except (LeagueNotFoundException, FantasyLeagueNotFoundException):
            self.fail("validate_available_leagues raised an exception unexpectedly")

    @patch(f'{BASE_CRUD_PATH}.get_leagues')
    def test_validate_available_leagues_league_not_found_exception(self, mock_get_leagues):
        # Arrange
        riot_leagues = [
            LeagueModel(**riot_fixtures.league_1_fixture.model_dump()),
            LeagueModel(**riot_fixtures.league_2_fixture.model_dump())
        ]
        mock_get_leagues.return_value = riot_leagues
        selected_league_ids = ["badId"]

        # Act and Assert
        with self.assertRaises(LeagueNotFoundException) as context:
            fantasy_league_util.validate_available_leagues(selected_league_ids)
        self.assertIn("badId not found", str(context.exception))

    @patch(f'{BASE_CRUD_PATH}.get_leagues')
    def test_validate_available_leagues_single_league_fantasy_unavailable_exception(
            self, mock_get_leagues):
        # Arrange
        riot_leagues = [
            LeagueModel(**riot_fixtures.league_1_fixture.model_dump()),
            LeagueModel(**riot_fixtures.league_2_fixture.model_dump())
        ]
        mock_get_leagues.return_value = riot_leagues
        selected_league_ids = [riot_fixtures.league_1_fixture.id]

        # Act and Assert
        with self.assertRaises(FantasyUnavailableException) as context:
            fantasy_league_util.validate_available_leagues(selected_league_ids)
        self.assertIn(f"{riot_fixtures.league_1_fixture.id} not available", str(context.exception))
        self.assertFalse(riot_fixtures.league_1_fixture.fantasy_available)
        self.assertTrue(riot_fixtures.league_2_fixture.fantasy_available)

    @patch(f'{BASE_CRUD_PATH}.get_leagues')
    def test_validate_available_leagues_multiple_leagues_fantasy_unavailable_exception(
            self, mock_get_leagues):
        # Arrange
        riot_leagues = [
            LeagueModel(**riot_fixtures.league_1_fixture.model_dump()),
            LeagueModel(**riot_fixtures.league_2_fixture.model_dump())
        ]
        mock_get_leagues.return_value = riot_leagues
        selected_league_ids = [riot_fixtures.league_1_fixture.id, riot_fixtures.league_2_fixture.id]

        # Act and Assert
        with self.assertRaises(FantasyUnavailableException) as context:
            fantasy_league_util.validate_available_leagues(selected_league_ids)
        self.assertIn(f"{riot_fixtures.league_1_fixture.id} not available", str(context.exception))
        self.assertFalse(riot_fixtures.league_1_fixture.fantasy_available)
        self.assertTrue(riot_fixtures.league_2_fixture.fantasy_available)

    @patch(f'{BASE_CRUD_PATH}.update_fantasy_league_current_draft_position')
    def test_update_fantasy_leagues_current_draft_position_increment_by_1(
            self, mock_update_fantasy_league_current_draft_position):
        # Arrange
        fantasy_league = create_fantasy_league_model(FantasyLeagueStatus.DRAFT, 0)
        fantasy_league.current_draft_position = 1
        expected_new_draft_position = fantasy_league.current_draft_position + 1

        # Act and Assert
        fantasy_league_util.update_fantasy_leagues_current_draft_position(fantasy_league)
        mock_update_fantasy_league_current_draft_position.assert_called_once_with(
            fantasy_league.id, expected_new_draft_position
        )
        self.assertTrue(expected_new_draft_position <= fantasy_league.number_of_teams)

    @patch(f'{BASE_CRUD_PATH}.update_fantasy_league_current_draft_position')
    def test_update_fantasy_leagues_current_draft_position_rollover_to_1(
            self, mock_update_fantasy_league_current_draft_position):
        # Arrange
        fantasy_league = create_fantasy_league_model(FantasyLeagueStatus.DRAFT, 0)
        fantasy_league.current_draft_position = fantasy_league.number_of_teams
        expected_new_draft_position = 1

        # Act and Assert
        fantasy_league_util.update_fantasy_leagues_current_draft_position(fantasy_league)
        mock_update_fantasy_league_current_draft_position.assert_called_once_with(
            fantasy_league.id, expected_new_draft_position
        )

    @patch(f'{BASE_CRUD_PATH}.update_fantasy_league_current_draft_position')
    def test_update_fantasy_leagues_current_draft_position_to_max_num_of_teams(
            self, mock_update_fantasy_league_current_draft_position):
        # Arrange
        fantasy_league = create_fantasy_league_model(FantasyLeagueStatus.DRAFT, 0)
        fantasy_league.current_draft_position = fantasy_league.number_of_teams - 1
        expected_new_draft_position = fantasy_league.number_of_teams

        # Act and Assert
        fantasy_league_util.update_fantasy_leagues_current_draft_position(fantasy_league)
        mock_update_fantasy_league_current_draft_position.assert_called_once_with(
            fantasy_league.id, expected_new_draft_position
        )


def create_fantasy_league_model(status: FantasyLeagueStatus, week: int):
    return FantasyLeagueModel(
        id=str(uuid.uuid4()),
        owner_id=fantasy_fixtures.user_fixture.id,
        status=status,
        name="Fantasy League Model Fixture",
        number_of_teams=6,
        current_draft_position=1,
        current_week=week
    )
