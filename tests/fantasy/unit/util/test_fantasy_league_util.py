from unittest.mock import patch
import uuid

from tests.test_base import FantasyLolTestBase
from tests.test_util import fantasy_fixtures

from src.db.models import (
    FantasyLeagueModel
)
from src.fantasy.exceptions.fantasy_league_not_found_exception import \
    FantasyLeagueNotFoundException
from src.fantasy.exceptions.fantasy_league_invalid_required_state_exception import \
    FantasyLeagueInvalidRequiredStateException
from src.fantasy.util.fantasy_league_util import FantasyLeagueUtil
from src.common.schemas.fantasy_schemas import (
    FantasyLeagueStatus
)

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


def create_fantasy_league_model(status: FantasyLeagueStatus, week: int):
    return FantasyLeagueModel(
        id=str(uuid.uuid4()),
        owner_id=fantasy_fixtures.user_fixture.id,
        status=status,
        name="Fantasy League Model Fixture",
        number_of_teams=6,
        current_week=week
    )
