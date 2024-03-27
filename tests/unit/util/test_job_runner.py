from tests.fantasy_lol_test_base import FantasyLolTestBase

from unittest.mock import MagicMock, patch
from common.exceptions.fantasy_lol_exception import FantasyLolException
from riot.util.job_runner import JobRunner

JOB_RUNNER_PATH = 'riot.util.job_runner'


class TestJobRunner(FantasyLolTestBase):
    def test_run_retry_job_successful(self):
        # Arrange
        job_function_mock = MagicMock()

        # Act
        JobRunner.run_retry_job(job_function_mock, "TestJob", max_retries=3)

        # Assert
        job_function_mock.assert_called_once()

    @patch('time.sleep', return_value=None)
    def test_run_retry_job_with_exception_then_success(self, sleep_mock):
        # Arrange
        job_function_mock = MagicMock()
        job_function_mock.side_effect = [FantasyLolException("Test exception"), None]
        job_name = "TestJob"
        max_retries = 1

        # Act
        JobRunner.run_retry_job(job_function_mock, job_name, max_retries)

        # Assert
        job_function_mock.assert_called_with()
        self.assertEqual(job_function_mock.call_count, max_retries + 1)
        sleep_mock.assert_called_once()

    @patch('time.sleep', return_value=None)
    def test_run_retry_job_with_max_retries_exceeded(self, sleep_mock):
        # Arrange
        exception_message = "Test exception"
        job_function_mock = MagicMock(side_effect=FantasyLolException(exception_message))
        job_name = "TestJob"
        max_retries = 2

        # Act
        with patch(f'{JOB_RUNNER_PATH}.logger.error') as log_error_mock:
            JobRunner.run_retry_job(job_function_mock, job_name, max_retries)

        # Assert
        job_function_mock.assert_called_with()
        self.assertEqual(job_function_mock.call_count, max_retries + 1)
        self.assertEqual(sleep_mock.call_count, max_retries)
        log_error_mock.assert_called_once_with(f'{job_name} failed: {exception_message}')
