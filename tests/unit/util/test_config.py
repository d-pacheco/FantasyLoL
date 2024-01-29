import unittest
from typing import Dict

from unittest.mock import patch
from fantasylol.exceptions.AppConfigException import AppConfigException
from fantasylol.util.config import AppConfig


def add_required_fields(env_vars: dict, required_fields: dict) -> Dict[str, str]:
    merged_env_vars = env_vars.copy()
    merged_env_vars.update(required_fields)
    return merged_env_vars


class TestAppConfig(unittest.TestCase):

    def setUp(self):
        self.required_fields = {
            'SECRET': '12345',
            'ALGORITHM': 'HS256'
        }

    @patch.dict('os.environ', {'DATABASE_URL': 'test_db_url'})
    def test_init_with_valid_env_variables(self):
        # Arrange
        base_env = {
            'DATABASE_URL': 'test_db_url',
            'DEBUG_LOGGING': 'True',
            'RIOT_API_KEY': 'test_riot_api_key',
            'ESPORTS_API_URL': 'test_esports_api_url',
            'ESPORTS_FEED_URL': 'test_esports_feed_url',
            'LEAGUE_SERVICE_SCHEDULE': '{"trigger": "cron", "hour": "10", "minute": "00"}'
        }

        valid_env = add_required_fields(base_env, self.required_fields)

        # Act
        config = AppConfig(valid_env)

        # Assert
        self.assertEqual(config.DATABASE_URL, 'test_db_url')
        self.assertTrue(config.DEBUG_LOGGING)
        self.assertEqual(config.RIOT_API_KEY, 'test_riot_api_key')
        self.assertEqual(config.ESPORTS_API_URL, 'test_esports_api_url')
        self.assertEqual(config.ESPORTS_FEED_URL, 'test_esports_feed_url')
        self.assertEqual(
            config.LEAGUE_SERVICE_SCHEDULE, {"trigger": "cron", "hour": "10", "minute": "00"}
        )

    def test_init_with_missing_required_field(self):
        # Arrange
        invalid_env = {}

        # Act & Assert
        with self.assertRaises(AppConfigException):
            AppConfig(invalid_env)

    def test_init_with_invalid_value(self):
        # Arrange
        base_env = {'LEAGUE_SERVICE_SCHEDULE': 'not_a_dict'}
        invalid_env = add_required_fields(base_env, self.required_fields)

        # Act & Assert
        with self.assertRaises(AppConfigException) as context:
            AppConfig(invalid_env)

        self.assertIn('Unable to cast value of "not_a_dict" to type "<class \'dict\'>" for '
                      '"LEAGUE_SERVICE_SCHEDULE" field', str(context.exception)
                      )

    def test_init_with_dict_type_field(self):
        # Arrange
        base_env = {'LEAGUE_SERVICE_SCHEDULE': '{"trigger": "cron", "hour": "10", "minute": "00"}'}
        valid_env = add_required_fields(base_env, self.required_fields)

        # Act
        config = AppConfig(valid_env)

        # Assert
        self.assertEqual(
            config.LEAGUE_SERVICE_SCHEDULE, {"trigger": "cron", "hour": "10", "minute": "00"}
        )

    def test_repr_method(self):
        # Arrange
        base_env = {'DATABASE_URL': 'test_db_url', 'DEBUG_LOGGING': 'True'}
        valid_env = add_required_fields(base_env, self.required_fields)

        # Act
        config = AppConfig(valid_env)
        repr_result = repr(config)

        # Assert
        self.assertIn("'DATABASE_URL': 'test_db_url'", repr_result)
        self.assertIn("'DEBUG_LOGGING': True", repr_result)
