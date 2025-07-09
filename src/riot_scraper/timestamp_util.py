from datetime import datetime, timedelta, timezone


class TimestampUtil:
    @staticmethod
    def round_current_time_to_10_seconds() -> str:
        current_time = datetime.now(timezone.utc)
        time_60_seconds_ago = current_time - timedelta(minutes=1)
        rounded_seconds = round(time_60_seconds_ago.second // 10) * 10
        rounded_time = time_60_seconds_ago.replace(second=rounded_seconds, microsecond=0)
        formatted_time = rounded_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return formatted_time

    @staticmethod
    def round_to_10_seconds(timestamp):
        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        rounded_seconds = round(dt.second / 10) * 10
        rounded_dt = dt.replace(second=rounded_seconds, microsecond=0)
        return rounded_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @staticmethod
    def parse_iso8601(timestamp_str):
        return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    @staticmethod
    def add_10_seconds(timestamp):
        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        dt += timedelta(seconds=10)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @staticmethod
    def parse_rfc3339(timestamp: str) -> datetime:
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",  # with milliseconds
            "%Y-%m-%dT%H:%M:%SZ",  # without milliseconds
        ]
        for fmt in formats:
            try:
                return datetime.strptime(timestamp, fmt)
            except ValueError:
                continue
        raise ValueError(f"Timestamp '{timestamp}' is not in a supported format.")
