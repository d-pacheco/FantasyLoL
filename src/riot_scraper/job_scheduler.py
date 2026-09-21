import atexit
from datetime import datetime
import logging

from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from apscheduler.triggers.cron import CronTrigger  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED  # type: ignore

from src.common import app_config
from src.common.config import ScheduleConfig
from src.riot.exceptions import JobConfigException

logger = logging.getLogger("scraper.scheduler")


class JobScheduler:
    def __init__(self, *args, **kwargs):
        self.riot_game_service = kwargs.get("game_service")
        self.riot_game_stats_service = kwargs.get("game_stats_service")
        self.riot_league_service = kwargs.get("league_service")
        self.riot_match_service = kwargs.get("match_service")
        self.riot_team_service = kwargs.get("team_service")
        self.riot_tournament_service = kwargs.get("tournament_service")
        self.game_analysis_service = kwargs.get("game_analysis_service")

        self.scheduler = BackgroundScheduler()
        # Surface job exceptions/misses in the scraper logs. APScheduler logs these
        # under the "apscheduler.*" logger tree, which has no handlers configured, so
        # without this listener a failing job (e.g. the match sync) dies silently.
        self.scheduler.add_listener(self._on_job_event, EVENT_JOB_ERROR | EVENT_JOB_MISSED)
        self.scheduler.start()
        atexit.register(self.shutdown_jobs)

    def _on_job_event(self, event):
        exc = getattr(event, "exception", None)
        if exc:
            logger.error(
                "Job '%s' raised an exception:\n%s\n%s",
                event.job_id,
                self._summarize_exception(exc),
                event.traceback,
            )
        else:
            logger.warning(
                f"Job '{event.job_id}' missed its scheduled run "
                f"(scheduled: {getattr(event, 'scheduled_run_time', 'unknown')})"
            )

    @staticmethod
    def _summarize_exception(exc: BaseException) -> str:
        """Build a concise, high-signal summary of an exception.

        The full ``event.traceback`` can be very long (SQLAlchemy embeds the SQL
        statement and bound parameters), and long multi-line messages sometimes get
        truncated by the log pipeline before the terminal exception line is reached.
        Emitting this summary first guarantees the real cause is visible. For database
        errors the driver exception (``.orig``) carries the Postgres ``DETAIL`` line
        (e.g. which key violated a unique constraint), so it is surfaced explicitly.
        """
        lines = [f"{type(exc).__name__}: {exc}"]

        # SQLAlchemy wraps the underlying DBAPI error on `.orig`.
        orig = getattr(exc, "orig", None)
        if orig is not None and orig is not exc:
            lines.append(f"Driver error: {type(orig).__name__}: {orig}")

        cause = exc.__cause__ or exc.__context__
        if cause is not None and cause is not exc and cause is not orig:
            lines.append(f"Caused by: {type(cause).__name__}: {cause}")

        return "\n".join(lines)

    def trigger_league_service_job(self):
        job = self.scheduler.get_job("league_service_job")
        if job:
            job.modify(next_run_time=datetime.now())

    def trigger_update_game_states_job(self):
        job = self.scheduler.get_job("update_game_states_job")
        if job:
            job.modify(next_run_time=datetime.now())

    def trigger_games_from_match_ids_job(self):
        job = self.scheduler.get_job("games_from_match_ids_job")
        if job:
            job.modify(next_run_time=datetime.now())

    def trigger_team_service_job(self):
        job = self.scheduler.get_job("team_service_job")
        if job:
            job.modify(next_run_time=datetime.now())

    def trigger_tournament_service_job(self):
        job = self.scheduler.get_job("tournament_service_job")
        if job:
            job.modify(next_run_time=datetime.now())

    def trigger_match_service_job(self):
        job = self.scheduler.get_job("match_service_job")
        if job:
            job.modify(next_run_time=datetime.now())

    def trigger_game_analysis_job(self):
        job = self.scheduler.get_job("game_analysis_job")
        if job:
            job.modify(next_run_time=datetime.now())

    def print_jobs(self):
        self.scheduler.print_jobs()

    def _run_match_jobs(self):
        # Each step is isolated so a failure in one (e.g. schedule sync hitting a
        # bad API response) is logged and does not silently skip the others.
        for step_name, step in (
            ("sync_schedule", self.riot_match_service.sync_schedule),
            ("backfill_event_details", self.riot_match_service.backfill_event_details),
            ("refresh_stale_events", self.riot_match_service.refresh_stale_events),
        ):
            try:
                step()
            except Exception:
                logger.exception(f"Match job step '{step_name}' failed")

    def schedule_all_jobs(self):
        logger.info("Scheduling jobs")

        self.schedule_job(
            job_function=self.riot_league_service.fetch_leagues_from_riot_retry_job,
            job_config=app_config.LEAGUE_SERVICE_SCHEDULE,
            job_id="league_service_job",
        )
        self.schedule_job(
            job_function=self.riot_tournament_service.fetch_tournaments_retry_job,
            job_config=app_config.TOURNAMENT_SERVICE_SCHEDULE,
            job_id="tournament_service_job",
        )
        self.schedule_job(
            job_function=self.riot_team_service.fetch_professional_teams_from_riot_retry_job,
            job_config=app_config.TEAM_SERVICE_SCHEDULE,
            job_id="team_service_job",
        )
        self.schedule_job(
            job_function=self._run_match_jobs,
            job_config=app_config.MATCH_SERVICE_SCHEDULE,
            job_id="match_service_job",
        )
        self.schedule_job(
            job_function=self.riot_game_service.fetch_games_from_match_ids_retry_job,
            job_config=app_config.GAME_SERVICE_SCHEDULE,
            job_id="games_from_match_ids_job",
        )
        self.schedule_job(
            job_function=self.riot_game_service.update_game_states_retry_job,
            job_config=app_config.GAME_SERVICE_SCHEDULE,
            job_id="update_game_states_job",
        )
        self.schedule_job(
            job_function=self.riot_game_stats_service.run_player_metadata_retry_job,
            job_config=app_config.GAME_STATS_SERVICE_SCHEDULE,
            job_id="player_metadata_job",
        )
        self.schedule_job(
            job_function=self.riot_game_stats_service.run_player_stats_retry_job,
            job_config=app_config.GAME_STATS_SERVICE_SCHEDULE,
            job_id="player_stats_job",
        )
        if self.game_analysis_service:
            self.schedule_job(
                job_function=self.game_analysis_service.analyze_games_retry_job,
                job_config=app_config.GAME_ANALYSIS_SERVICE_SCHEDULE,
                job_id="game_analysis_job",
            )

    def schedule_job(
        self, job_function, job_config: ScheduleConfig, job_id: str, replace: bool = True
    ):
        if job_config.trigger == "cron":
            job_trigger = CronTrigger(
                day=job_config.day,
                week=job_config.week,
                hour=job_config.hour,
                minute=job_config.minute,
                second=job_config.second,
            )
        elif job_config.trigger == "interval":
            job_trigger = IntervalTrigger(
                weeks=job_config.weeks,
                days=job_config.days,
                hours=job_config.hours,
                minutes=job_config.minutes,
                seconds=job_config.seconds,
            )
        else:
            raise JobConfigException(
                f"Invalid trigger ({job_config.trigger}) " f"when scheduling job with id: {job_id}"
            )

        self.scheduler.add_job(
            job_function, trigger=job_trigger, id=job_id, replace_existing=replace
        )

    def shutdown_jobs(self):
        logger.info("Shutting down scheduled jobs")
        self.scheduler.shutdown()
