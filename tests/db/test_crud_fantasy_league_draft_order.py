from sqlalchemy.exc import IntegrityError

from tests.test_base import FantasyLolTestBase
from tests.test_util import fantasy_fixtures

from src.db import crud

from src.common.schemas.fantasy_schemas import FantasyLeagueDraftOrder


class TestCrudFantasyLeagueDraftOrder(FantasyLolTestBase):
    def test_create_and_get_fantasy_league_draft_order(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user = fantasy_fixtures.user_fixture
        draft_order = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id,
            user_id=user.id,
            position=1
        )

        # Act and Assert
        draft_order_before_create = crud.get_fantasy_league_draft_order(fantasy_league.id)
        self.assertEqual(0, len(draft_order_before_create))
        crud.create_fantasy_league_draft_order(draft_order)
        draft_order_after_create = crud.get_fantasy_league_draft_order(fantasy_league.id)
        self.assertEqual(1, len(draft_order_after_create))
        self.assertEqual(draft_order, draft_order_after_create[0])
        with self.assertRaises(IntegrityError) as context:
            crud.create_fantasy_league_draft_order(draft_order)
        self.assertIn(
            'UNIQUE constraint failed: fantasy_league_draft_order.fantasy_league_id, '
            'fantasy_league_draft_order.user_id',
            str(context.exception)
        )

    def test_delete_fantasy_league_draft_order(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user = fantasy_fixtures.user_fixture
        draft_order = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id,
            user_id=user.id,
            position=1
        )
        crud.create_fantasy_league_draft_order(draft_order)

        # Act and Assert
        draft_order_before_delete = crud.get_fantasy_league_draft_order(fantasy_league.id)
        self.assertEqual(1, len(draft_order_before_delete))
        crud.delete_fantasy_league_draft_order(draft_order)
        draft_order_after_delete = crud.get_fantasy_league_draft_order(fantasy_league.id)
        self.assertEqual(0, len(draft_order_after_delete))
        with self.assertRaises(AssertionError):
            crud.delete_fantasy_league_draft_order(draft_order)

    def test_update_fantasy_league_draft_order_position(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        user = fantasy_fixtures.user_fixture
        draft_order = FantasyLeagueDraftOrder(
            fantasy_league_id=fantasy_league.id,
            user_id=user.id,
            position=1
        )
        crud.create_fantasy_league_draft_order(draft_order)
        new_position = 2
        updated_draft_order = draft_order.model_copy(deep=True)
        updated_draft_order.position = new_position

        # Act and Assert
        self.assertNotEqual(draft_order.position, new_position)
        draft_order_before_update = crud.get_fantasy_league_draft_order(fantasy_league.id)
        self.assertEqual(1, len(draft_order_before_update))
        self.assertEqual(draft_order, draft_order_before_update[0])
        crud.update_fantasy_league_draft_order_position(draft_order, new_position)
        draft_order_after_update = crud.get_fantasy_league_draft_order(fantasy_league.id)
        self.assertEqual(1, len(draft_order_after_update))
        self.assertEqual(updated_draft_order, draft_order_after_update[0])
