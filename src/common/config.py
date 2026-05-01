from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ScheduleConfig(BaseModel):
    trigger: str
    day: str | None = None
    week: str | None = None
    hour: str | None = None
    minute: str | None = None
    second: str | None = None
    # interval fields
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/fantasy_lol"
    DEBUG_LOGGING: bool = False

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Auth
    AUTH_SECRET: str
    AUTH_ALGORITHM: str = "HS256"

    # Email verification
    REQUIRE_EMAIL_VERIFICATION: bool = True

    # Riot API
    RIOT_API_KEY: str = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"
    ESPORTS_API_URL: str = "https://esports-api.lolesports.com/persisted/gw"
    ESPORTS_FEED_URL: str = "https://feed.lolesports.com/livestats/v1"

    # Job schedules
    LEAGUE_SERVICE_SCHEDULE: ScheduleConfig = ScheduleConfig(trigger="cron", hour="10", minute="00")
    TOURNAMENT_SERVICE_SCHEDULE: ScheduleConfig = ScheduleConfig(
        trigger="cron", hour="10", minute="05"
    )
    TEAM_SERVICE_SCHEDULE: ScheduleConfig = ScheduleConfig(trigger="cron", hour="10", minute="10")
    MATCH_SERVICE_SCHEDULE: ScheduleConfig = ScheduleConfig(trigger="cron", minute="30")
    GAME_SERVICE_SCHEDULE: ScheduleConfig = ScheduleConfig(trigger="cron", minute="45")
    GAME_STATS_SERVICE_SCHEDULE: ScheduleConfig = ScheduleConfig(trigger="cron", minute="*/5")


app_config = AppConfig()  # type: ignore[call-arg]
