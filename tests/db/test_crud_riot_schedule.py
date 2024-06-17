from src.db import crud
from tests.test_base import FantasyLolTestBase
from tests.test_util import riot_fixtures


class TestCrudRiotSchedule(FantasyLolTestBase):
    def test_get_schedule_exists(self):
        # Arrange
        schedule = riot_fixtures.riot_schedule_fixture
        crud.update_schedule(schedule)

        # Act
        schedule_from_db = crud.get_schedule(schedule.schedule_name)

        # Assert
        self.assertEqual(schedule, schedule_from_db)

    def test_get_schedule_does_not_exist(self):
        # Arrange
        schedule = riot_fixtures.riot_schedule_fixture
        crud.update_schedule(schedule)

        # Act
        schedule_from_db = crud.get_schedule("bad_schedule_name")

        # Assert
        self.assertIsNone(schedule_from_db)

    def test_update_schedule_no_existing_schedule(self):
        # Arrange
        schedule = riot_fixtures.riot_schedule_fixture

        # Act and Assert
        schedule_from_db_before_update_call = crud.get_schedule(schedule.schedule_name)
        self.assertIsNone(schedule_from_db_before_update_call)
        crud.update_schedule(schedule)
        schedule_from_db_after_update_call = crud.get_schedule(schedule.schedule_name)
        self.assertEqual(schedule, schedule_from_db_after_update_call)

    def test_update_schedule_with_existing_schedule(self):
        # Arrange
        schedule = riot_fixtures.riot_schedule_fixture
        crud.update_schedule(schedule)
        updated_schedule = schedule.model_copy(deep=True)
        updated_schedule.current_token_key = "updated_current_token"
        updated_schedule.older_token_key = "updated_older_token"

        # Act and Assert
        schedule_from_db_before_update_call = crud.get_schedule(schedule.schedule_name)
        self.assertEqual(schedule, schedule_from_db_before_update_call)
        crud.update_schedule(updated_schedule)
        schedule_from_db_after_update_call = crud.get_schedule(schedule.schedule_name)
        self.assertEqual(updated_schedule, schedule_from_db_after_update_call)
        self.assertEqual(schedule.schedule_name, updated_schedule.schedule_name)
