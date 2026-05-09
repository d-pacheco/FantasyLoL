from datetime import datetime, timezone, timedelta

from src.riot_scraper.timestamp_util import TimestampUtil


class TestTimestampUtil:
    def test_round_current_time_is_at_least_10_minutes_old(self):
        result = TimestampUtil.round_current_time_to_10_seconds()
        parsed = datetime.strptime(result, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        age = now - parsed
        assert age >= timedelta(minutes=10)

    def test_round_current_time_is_not_more_than_12_minutes_old(self):
        result = TimestampUtil.round_current_time_to_10_seconds()
        parsed = datetime.strptime(result, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        age = now - parsed
        assert age <= timedelta(minutes=12)

    def test_round_current_time_seconds_are_multiple_of_10(self):
        result = TimestampUtil.round_current_time_to_10_seconds()
        parsed = datetime.strptime(result, "%Y-%m-%dT%H:%M:%S.%fZ")
        assert parsed.second % 10 == 0

    def test_round_current_time_has_zero_microseconds(self):
        result = TimestampUtil.round_current_time_to_10_seconds()
        parsed = datetime.strptime(result, "%Y-%m-%dT%H:%M:%S.%fZ")
        assert parsed.microsecond == 0

    def test_round_to_10_seconds_with_seconds_above_55(self):
        """Seconds >= 55 should floor to 50, not round up to 60."""
        result = TimestampUtil.round_to_10_seconds("2024-01-01T00:00:57.123456Z")
        assert result == "2024-01-01T00:00:50.000000Z"

    def test_round_to_10_seconds_result_is_valid(self):
        result = TimestampUtil.round_to_10_seconds("2024-01-01T12:34:59.999999Z")
        parsed = datetime.strptime(result, "%Y-%m-%dT%H:%M:%S.%fZ")
        assert 0 <= parsed.second <= 59
