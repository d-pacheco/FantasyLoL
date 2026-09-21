from datetime import datetime, timedelta, timezone

# Riot's rfc460Timestamp is sometimes returned with fractional seconds
# (e.g. "2024-01-01T00:00:57.123456Z") and sometimes without
# (e.g. "2024-01-01T00:00:57Z"). Parsing must tolerate both.
_SUPPORTED_FORMATS = (
    "%Y-%m-%dT%H:%M:%S.%fZ",  # with fractional seconds
    "%Y-%m-%dT%H:%M:%SZ",  # without fractional seconds
)


class TimestampUtil:
    @staticmethod
    def _parse(timestamp: str) -> datetime:
        for fmt in _SUPPORTED_FORMATS:
            try:
                return datetime.strptime(timestamp, fmt)
            except ValueError:
                continue
        raise ValueError(f"Timestamp '{timestamp}' is not in a supported format.")

    @staticmethod
    def round_current_time_to_10_seconds() -> str:
        current_time = datetime.now(timezone.utc)
        time_ago = current_time - timedelta(minutes=11)
        rounded_seconds = round(time_ago.second // 10) * 10
        rounded_time = time_ago.replace(second=rounded_seconds, microsecond=0)
        formatted_time = rounded_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return formatted_time

    @staticmethod
    def round_to_10_seconds(timestamp):
        dt = TimestampUtil._parse(timestamp)
        rounded_seconds = (dt.second // 10) * 10
        rounded_dt = dt.replace(second=rounded_seconds, microsecond=0)
        return rounded_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @staticmethod
    def parse_iso8601(timestamp_str):
        return TimestampUtil._parse(timestamp_str)

    @staticmethod
    def add_10_seconds(timestamp):
        dt = TimestampUtil._parse(timestamp)
        dt += timedelta(seconds=10)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @staticmethod
    def parse_rfc3339(timestamp: str) -> datetime:
        return TimestampUtil._parse(timestamp)
