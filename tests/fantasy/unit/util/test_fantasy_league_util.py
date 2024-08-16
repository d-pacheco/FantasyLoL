from unittest.mock import MagicMock, call

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures, riot_fixtures

from src.common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueDraftOrder,
    FantasyLeagueDraftOrderResponse,
    FantasyLeagueStatus,
    FantasyLeagueID,
    UserID
)
from src.common.schemas.riot_data_schemas import RiotLeagueID
from src.common.exceptions import LeagueNotFoundException

from src.fantasy.exceptions import (
    DraftOrderException,
    FantasyLeagueNotFoundException,
    FantasyLeagueInvalidRequiredStateException,
    FantasyUnavailableException
)
from src.fantasy.util import FantasyLeagueUtil


class TestFantasyLeagueUtil(TestBase):
    def setUp(self):
        self.mock_db_service = MagicMock()
        self.fantasy_league_util = FantasyLeagueUtil(self.mock_db_service)

    def tearDown(self):
        self.mock_db_service.reset_mock()

    def test_validate_league_successful(self):
        # Arrange
        expected_fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = expected_fantasy_league
        required_states = [FantasyLeagueStatus.DRAFT]


        # Act
        returned_fantasy_league = self.fantasy_league_util.validate_league(
            expected_fantasy_league.id, required_states
        )

        # Assert
        self.assertEqual(expected_fantasy_league, returned_fantasy_league)
        self.assertIsInstance(returned_fantasy_league, FantasyLeague)
        self.assertIn(expected_fantasy_league.status, required_states)
        self.mock_db_service.get_fantasy_league_by_id.assert_called_once_with(expected_fantasy_league.id)

    def test_validate_league_league_not_found_exception(self):
        # Arrange
        self.mock_db_service.get_fantasy_league_by_id.return_value = None

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_util.validate_league(
                FantasyLeagueID("someId"), [FantasyLeagueStatus.DRAFT]
            )

    def test_validate_league_not_in_required_state(self):
        # Arrange
        expected_fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = expected_fantasy_league
        required_states = [FantasyLeagueStatus.DRAFT]

        # Act and Assert
        with self.assertRaises(FantasyLeagueInvalidRequiredStateException):
            self.fantasy_league_util.validate_league(expected_fantasy_league.id, required_states)
        self.assertNotIn(expected_fantasy_league.status, required_states)

    def test_validate_league_no_required_state_should_return_fantasy_league_if_it_exists(self):
        # Arrange
        expected_fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = expected_fantasy_league

        # Act
        returned_fantasy_league = self.fantasy_league_util.validate_league(expected_fantasy_league.id)

        # Assert
        self.assertEqual(expected_fantasy_league, returned_fantasy_league)
        self.assertIsInstance(returned_fantasy_league, FantasyLeague)

    def test_validate_available_leagues_successful(self):
        # Arrange
        riot_leagues = [riot_fixtures.league_1_fixture, riot_fixtures.league_2_fixture]
        self.mock_db_service.get_leagues.return_value = riot_leagues
        selected_league_ids = [riot_fixtures.league_2_fixture.id]

        # Act and Assert
        try:
            self.fantasy_league_util.validate_available_leagues(selected_league_ids)
        except (LeagueNotFoundException, FantasyLeagueNotFoundException):
            self.fail("validate_available_leagues raised an exception unexpectedly")

    def test_validate_available_leagues_league_not_found_exception(self):
        # Arrange
        riot_leagues = [riot_fixtures.league_1_fixture, riot_fixtures.league_2_fixture]
        self.mock_db_service.get_leagues.return_value = riot_leagues
        selected_league_ids = [RiotLeagueID("badId")]

        # Act and Assert
        with self.assertRaises(LeagueNotFoundException) as context:
            self.fantasy_league_util.validate_available_leagues(selected_league_ids)
        self.assertIn("badId not found", str(context.exception))

    def test_validate_available_leagues_single_league_fantasy_unavailable_exception(self):
        # Arrange
        riot_leagues = [riot_fixtures.league_1_fixture, riot_fixtures.league_2_fixture]
        self.mock_db_service.get_leagues.return_value = riot_leagues
        selected_league_ids = [riot_fixtures.league_1_fixture.id]

        # Act and Assert
        with self.assertRaises(FantasyUnavailableException) as context:
            self.fantasy_league_util.validate_available_leagues(selected_league_ids)
        self.assertIn(f"{riot_fixtures.league_1_fixture.id} not available", str(context.exception))
        self.assertFalse(riot_fixtures.league_1_fixture.fantasy_available)
        self.assertTrue(riot_fixtures.league_2_fixture.fantasy_available)

    def test_validate_available_leagues_multiple_leagues_fantasy_unavailable_exception(self):
        # Arrange
        riot_leagues = [riot_fixtures.league_1_fixture, riot_fixtures.league_2_fixture]
        self.mock_db_service.get_leagues.return_value = riot_leagues
        selected_league_ids = [riot_fixtures.league_1_fixture.id, riot_fixtures.league_2_fixture.id]

        # Act and Assert
        with self.assertRaises(FantasyUnavailableException) as context:
            self.fantasy_league_util.validate_available_leagues(selected_league_ids)
        self.assertIn(f"{riot_fixtures.league_1_fixture.id} not available", str(context.exception))
        self.assertFalse(riot_fixtures.league_1_fixture.fantasy_available)
        self.assertTrue(riot_fixtures.league_2_fixture.fantasy_available)

    def test_update_fantasy_leagues_current_draft_position_increment_by_1(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture.model_copy()
        fantasy_league.current_draft_position = 1
        expected_new_draft_position = fantasy_league.current_draft_position + 1

        # Act and Assert
        self.fantasy_league_util.update_fantasy_leagues_current_draft_position(fantasy_league)
        self.mock_db_service.update_fantasy_league_current_draft_position.assert_called_once_with(
            fantasy_league.id, expected_new_draft_position
        )
        self.assertTrue(expected_new_draft_position <= fantasy_league.number_of_teams)

    def test_update_fantasy_leagues_current_draft_position_rollover_to_1(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture.model_copy()
        fantasy_league.current_draft_position = fantasy_league.number_of_teams
        expected_new_draft_position = 1

        # Act and Assert
        self.fantasy_league_util.update_fantasy_leagues_current_draft_position(fantasy_league)
        self.mock_db_service.update_fantasy_league_current_draft_position.assert_called_once_with(
            fantasy_league.id, expected_new_draft_position
        )

    def test_update_fantasy_leagues_current_draft_position_to_max_num_of_teams(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_draft_fixture.model_copy()
        fantasy_league.current_draft_position = fantasy_league.number_of_teams - 1
        expected_new_draft_position = fantasy_league.number_of_teams

        # Act and Assert
        self.fantasy_league_util.update_fantasy_leagues_current_draft_position(fantasy_league)
        self.mock_db_service.update_fantasy_league_current_draft_position.assert_called_once_with(
            fantasy_league.id, expected_new_draft_position
        )

    def test_create_draft_order_entry_first_draft_order_for_fantasy_league(self,):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = fantasy_league
        self.mock_db_service.get_fantasy_league_draft_order.return_value = []
        expected_draft_order_entry = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id, user_id=user.id, position=1
        )

        # Act
        self.fantasy_league_util.create_draft_order_entry(user.id, fantasy_league.id)

        # Assert
        self.mock_db_service.get_fantasy_league_by_id.assert_called_once_with(fantasy_league.id)
        self.mock_db_service.get_fantasy_league_draft_order.assert_called_once_with(fantasy_league.id)
        self.mock_db_service.create_fantasy_league_draft_order.assert_called_once_with(
            expected_draft_order_entry
        )

    def test_create_draft_order_entry_with_an_existing_draft_entry(self,):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = fantasy_league
        self.mock_db_service.get_fantasy_league_draft_order.return_value = [
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=UserID("someOtherId"), position=1
            )
        ]
        expected_draft_order_entry = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id, user_id=user.id, position=2
        )

        # Act
        self.fantasy_league_util.create_draft_order_entry(user.id, fantasy_league.id)

        # Assert
        self.mock_db_service.get_fantasy_league_by_id.assert_called_once_with(fantasy_league.id)
        self.mock_db_service.get_fantasy_league_draft_order.assert_called_once_with(fantasy_league.id)
        self.mock_db_service.create_fantasy_league_draft_order.assert_called_once_with(expected_draft_order_entry)

    def test_create_draft_order_entry_fantasy_league_not_found_exception(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.mock_db_service.get_fantasy_league_by_id.return_value = None

        # Act and Assert
        with self.assertRaises(FantasyLeagueNotFoundException):
            self.fantasy_league_util.create_draft_order_entry(user.id, fantasy_league.id)
            self.mock_db_service.get_fantasy_league_by_id.assert_called_once_with(fantasy_league.id)
            self.mock_db_service.get_fantasy_league_draft_order.assert_not_called()
            self.mock_db_service.create_fantasy_league_draft_order.assert_not_called()

    def test_validate_draft_order_no_changes_successful(self):
        # Arrange
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        current_draft_order = [
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_1.id, position=1
            ),
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_2.id, position=2
            )
        ]
        updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=user_1.id, username=user_1.username, position=1
            ),
            FantasyLeagueDraftOrderResponse(
                user_id=user_2.id, username=user_2.username, position=2
            ),
        ]

        # Act and Assert
        try:
            self.fantasy_league_util.validate_draft_order(current_draft_order, updated_draft_order)
        except Exception:
            self.fail("Validate draft order got an unexpected exception")
        self.assertTrue(len(current_draft_order) == len(updated_draft_order))
        for i in range(len(current_draft_order)):
            self.assertEqual(current_draft_order[i].user_id, updated_draft_order[i].user_id)
            self.assertEqual(current_draft_order[i].position, updated_draft_order[i].position)

    def test_validate_draft_order_swapped_positions_successful(self):
        # Arrange
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        current_draft_order = [
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_1.id, position=1
            ),
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_2.id, position=2
            )
        ]
        updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=user_1.id, username=user_1.username, position=2
            ),
            FantasyLeagueDraftOrderResponse(
                user_id=user_2.id, username=user_2.username, position=1
            ),
        ]

        # Act and Assert
        try:
            self.fantasy_league_util.validate_draft_order(current_draft_order, updated_draft_order)
        except Exception:
            self.fail("Validate draft order got an unexpected exception")
        self.assertTrue(len(current_draft_order) == len(updated_draft_order))
        for i in range(len(current_draft_order)):
            self.assertEqual(current_draft_order[i].user_id, updated_draft_order[i].user_id)
            self.assertNotEqual(current_draft_order[i].position, updated_draft_order[i].position)

    def test_validate_draft_order_too_few_entries_for_updated_draft_order_exception(self):
        # Arrange
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        current_draft_order = [
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_1.id, position=1
            ),
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_2.id, position=2
            )
        ]
        updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=user_1.id, username=user_1.username, position=1
            )
        ]

        # Act and Assert
        with self.assertRaises(DraftOrderException) as context:
            self.fantasy_league_util.validate_draft_order(current_draft_order, updated_draft_order)
        self.assertIn("Draft order contains more or less", str(context.exception))
        self.assertTrue(len(updated_draft_order) < len(current_draft_order))

    def test_validate_draft_order_too_many_entries_for_updated_draft_order_exception(self):
        # Arrange
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        user_3 = fantasy_fixtures.user_3_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        current_draft_order = [
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_1.id, position=1
            ),
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_2.id, position=2
            )
        ]
        updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=user_1.id, username=user_1.username, position=1
            ),
            FantasyLeagueDraftOrderResponse(
                user_id=user_2.id, username=user_2.username, position=2
            ),
            FantasyLeagueDraftOrderResponse(
                user_id=user_3.id, username=user_3.username, position=3
            )
        ]

        # Act and Assert
        with self.assertRaises(DraftOrderException) as context:
            self.fantasy_league_util.validate_draft_order(current_draft_order, updated_draft_order)
        self.assertIn("Draft order contains more or less", str(context.exception))
        self.assertTrue(len(updated_draft_order) > len(current_draft_order))

    def test_validate_draft_order_user_not_in_the_current_draft_exception(self):
        # Arrange
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        user_3 = fantasy_fixtures.user_3_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        current_draft_order = [
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_1.id, position=1
            ),
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_2.id, position=2
            )
        ]
        updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=user_1.id, username=user_1.username, position=1
            ),
            FantasyLeagueDraftOrderResponse(
                user_id=user_3.id, username=user_3.username, position=2
            )
        ]

        # Act and Assert
        with self.assertRaises(DraftOrderException) as context:
            self.fantasy_league_util.validate_draft_order(current_draft_order, updated_draft_order)
        self.assertIn(f"User {user_3.id} is not in current draft", str(context.exception))

    def test_validate_draft_order_invalid_positions_same_numbers_exception(self):
        # Arrange
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        current_draft_order = [
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_1.id, position=1
            ),
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_2.id, position=2
            )
        ]
        updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=user_1.id, username=user_1.username, position=1
            ),
            FantasyLeagueDraftOrderResponse(
                user_id=user_2.id, username=user_2.username, position=1
            )
        ]

        # Act and Assert
        with self.assertRaises(DraftOrderException) as context:
            self.fantasy_league_util.validate_draft_order(current_draft_order, updated_draft_order)
        self.assertIn(
            "The positions given in the updated draft order are not valid",
            str(context.exception)
        )

    def test_validate_draft_order_invalid_positions_negatives_of_positions_exception(self):
        # Arrange
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        current_draft_order = [
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_1.id, position=1
            ),
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_2.id, position=2
            )
        ]
        updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=user_1.id, username=user_1.username, position=-1
            ),
            FantasyLeagueDraftOrderResponse(
                user_id=user_2.id, username=user_2.username, position=-2
            )
        ]

        # Act and Assert
        with self.assertRaises(DraftOrderException) as context:
            self.fantasy_league_util.validate_draft_order(current_draft_order, updated_draft_order)
        self.assertIn(
            "The positions given in the updated draft order are not valid",
            str(context.exception)
        )

    def test_validate_draft_order_invalid_positions_gap_between_positions_exception(self):
        # Arrange
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        current_draft_order = [
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_1.id, position=1
            ),
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_2.id, position=2
            )
        ]
        updated_draft_order = [
            FantasyLeagueDraftOrderResponse(
                user_id=user_1.id, username=user_1.username, position=1
            ),
            FantasyLeagueDraftOrderResponse(
                user_id=user_2.id, username=user_2.username, position=3
            )
        ]

        # Act and Assert
        with self.assertRaises(DraftOrderException) as context:
            self.fantasy_league_util.validate_draft_order(current_draft_order, updated_draft_order)
        self.assertIn(
            "The positions given in the updated draft order are not valid",
            str(context.exception)
        )

    def test_update_draft_order_on_player_leave_middle_position_successful(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        user_3 = fantasy_fixtures.user_3_fixture
        expected_position_to_delete = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id, user_id=user_2.id, position=2
        )
        user_id_to_remove = expected_position_to_delete.user_id
        current_draft_order = [
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_1.id, position=1
            ),
            expected_position_to_delete,
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_3.id, position=3
            )
        ]
        self.mock_db_service.get_fantasy_league_draft_order.return_value = current_draft_order

        # Act and Assert
        try:
            self.fantasy_league_util.update_draft_order_on_player_leave(
                user_id_to_remove, fantasy_league.id
            )
        except DraftOrderException:
            self.fail("Update draft order on player leave failed with an unexpected exception")
        self.mock_db_service.get_fantasy_league_draft_order.assert_called_once_with(fantasy_league.id)
        self.mock_db_service.delete_fantasy_league_draft_order.assert_called_once_with(expected_position_to_delete)
        self.mock_db_service.update_fantasy_league_draft_order_position.assert_called_once_with(
            current_draft_order[2], 2
        )

    def test_update_draft_order_on_player_leave_first_position_successful(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        user_3 = fantasy_fixtures.user_3_fixture
        expected_position_to_delete = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id, user_id=user_1.id, position=1
        )
        user_id_to_remove = expected_position_to_delete.user_id
        current_draft_order = [
            expected_position_to_delete,
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_2.id, position=2
            ),
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_3.id, position=3
            )
        ]
        self.mock_db_service.get_fantasy_league_draft_order.return_value = current_draft_order

        # Act and Assert
        try:
            self.fantasy_league_util.update_draft_order_on_player_leave(
                user_id_to_remove, fantasy_league.id
            )
        except DraftOrderException:
            self.fail("Update draft order on player leave failed with an unexpected exception")
        self.mock_db_service.get_fantasy_league_draft_order.assert_called_once_with(fantasy_league.id)
        self.mock_db_service.delete_fantasy_league_draft_order.assert_called_once_with(expected_position_to_delete)
        expected_calls = [
            call.update_fantasy_league_draft_order_position(current_draft_order[1], 1),
            call.update_fantasy_league_draft_order_position(current_draft_order[2], 2)
        ]
        self.mock_db_service.update_fantasy_league_draft_order_position.assert_has_calls(expected_calls)
        self.assertEqual(self.mock_db_service.update_fantasy_league_draft_order_position.call_count, 2)

    def test_update_draft_order_on_player_leave_last_position_successful(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        user_3 = fantasy_fixtures.user_3_fixture
        expected_position_to_delete = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id, user_id=user_3.id, position=3
        )
        user_id_to_remove = expected_position_to_delete.user_id
        current_draft_order = [
            expected_position_to_delete,
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_1.id, position=1
            ),
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_2.id, position=2
            )
        ]
        self.mock_db_service.get_fantasy_league_draft_order.return_value = current_draft_order

        # Act and Assert
        try:
            self.fantasy_league_util.update_draft_order_on_player_leave(
                user_id_to_remove, fantasy_league.id
            )
        except DraftOrderException:
            self.fail("Update draft order on player leave failed with an unexpected exception")
        self.mock_db_service.get_fantasy_league_draft_order.assert_called_once_with(fantasy_league.id)
        self.mock_db_service.delete_fantasy_league_draft_order.assert_called_once_with(expected_position_to_delete)
        self.mock_db_service.update_fantasy_league_draft_order_position.assert_not_called()

    def test_update_draft_order_on_player_leave_user_has_no_draft_position_exception(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user_1 = fantasy_fixtures.user_fixture
        user_2 = fantasy_fixtures.user_2_fixture
        user_3 = fantasy_fixtures.user_3_fixture
        current_draft_order = [
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_1.id, position=1
            ),
            FantasyLeagueDraftOrder(
                fantasy_league_id=fantasy_league.id, user_id=user_2.id, position=2
            )
        ]
        self.mock_db_service.get_fantasy_league_draft_order.return_value = current_draft_order

        # Act and Assert
        with self.assertRaises(DraftOrderException) as context:
            self.fantasy_league_util.update_draft_order_on_player_leave(user_3.id, fantasy_league.id)
        self.assertIn("Missing user on draft removal", str(context.exception))
        self.mock_db_service.get_fantasy_league_draft_order.assert_called_once_with(fantasy_league.id)
        self.mock_db_service.delete_fantasy_league_draft_order.assert_not_called()
        self.mock_db_service.update_fantasy_league_draft_order_position.assert_not_called()
