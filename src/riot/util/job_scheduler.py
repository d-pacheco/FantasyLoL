import atexit
from datetime import datetime
import logging

from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from apscheduler.triggers.cron import CronTrigger  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from src.common import app_config
from src.riot.exceptions import JobConfigException

logger = logging.getLogger('riot')


class JobScheduler:
    def __init__(self, *args, **kwargs):

        self.riot_game_service = kwargs.get('game_service')
        self.riot_game_stats_service = kwargs.get('game_stats_service')
        self.riot_league_service = kwargs.get('league_service')
        self.riot_match_service = kwargs.get('match_service')
        self.riot_player_service = kwargs.get('player_service')
        self.riot_team_service = kwargs.get('team_service')
        self.riot_tournament_service = kwargs.get('tournament_service')

        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        atexit.register(self.shutdown_jobs)

    def trigger_league_service_job(self):
        job = self.scheduler.get_job('league_service_job')
        if job:
            job.modify(next_run_time=datetime.now())

    def trigger_update_game_states_job(self):
        job = self.scheduler.get_job('update_game_states_job')
        if job:
            job.modify(next_run_time=datetime.now())

    def trigger_games_from_match_ids_job(self):
        job = self.scheduler.get_job('games_from_match_ids_job')
        if job:
            job.modify(next_run_time=datetime.now())

    def trigger_player_service_job(self):
        job = self.scheduler.get_job('player_service_job')
        if job:
            job.modify(next_run_time=datetime.now())

    def trigger_team_service_job(self):
        job = self.scheduler.get_job('team_service_job')
        if job:
            job.modify(next_run_time=datetime.now())

    def trigger_tournament_service_job(self):
        job = self.scheduler.get_job('tournament_service_job')
        if job:
            job.modify(next_run_time=datetime.now())

    def trigger_match_service_job(self):
        job = self.scheduler.get_job('match_service_job')
        if job:
            job.modify(next_run_time=datetime.now())

    def print_jobs(self):
        self.scheduler.print_jobs()

    def schedule_all_jobs(self):
        logger.info("Scheduling jobs")

        self.schedule_job(
            job_function=self.riot_league_service.fetch_leagues_from_riot_retry_job,
            job_config=app_config.LEAGUE_SERVICE_SCHEDULE,
            job_id='league_service_job',
        )
        self.schedule_job(
            job_function=self.riot_tournament_service.fetch_tournaments_retry_job,
            job_config=app_config.TOURNAMENT_SERVICE_SCHEDULE,
            job_id='tournament_service_job'
        )
        self.schedule_job(
            job_function=self.riot_team_service.fetch_professional_teams_from_riot_retry_job,
            job_config=app_config.TEAM_SERVICE_SCHEDULE,
            job_id='team_service_job'
        )
        self.schedule_job(
            job_function=self.riot_player_service.fetch_professional_players_from_riot_retry_job,
            job_config=app_config.PLAYER_SERVICE_SCHEDULE,
            job_id='player_service_job'
        )
        self.schedule_job(
            job_function=self.riot_match_service.fetch_new_schedule_retry_job,
            job_config=app_config.MATCH_SERVICE_SCHEDULE,
            job_id='match_service_job'
        )
        self.schedule_job(
            job_function=self.riot_game_service.fetch_games_from_match_ids_retry_job,
            job_config=app_config.GAME_SERVICE_SCHEDULE,
            job_id='games_from_match_ids_job'
        )
        self.schedule_job(
            job_function=self.riot_game_service.update_game_states_retry_job,
            job_config=app_config.GAME_SERVICE_SCHEDULE,
            job_id='update_game_states_job'
        )
        self.schedule_job(
            job_function=self.riot_game_stats_service.run_player_metadata_retry_job,
            job_config=app_config.GAME_STATS_SERVICE_SCHEDULE,
            job_id='player_metadata_job'
        )
        self.schedule_job(
            job_function=self.riot_game_stats_service.run_player_stats_retry_job,
            job_config=app_config.GAME_STATS_SERVICE_SCHEDULE,
            job_id='player_stats_job'
        )

    def schedule_job(self, job_function, job_config: dict, job_id: str, replace: bool = True):
        trigger = job_config.get('trigger', None)

        if trigger == 'cron':
            job_trigger = CronTrigger(
                day=job_config.get('day', None),
                week=job_config.get('week', None),
                hour=job_config.get('hour', None),
                minute=job_config.get('minute', None),
                second=job_config.get('second', None),
            )
        elif trigger == 'interval':
            job_trigger = IntervalTrigger(
                weeks=job_config.get('weeks', 0),
                days=job_config.get('days', 0),
                hours=job_config.get('hours', 0),
                minutes=job_config.get('minutes', 0),
                seconds=job_config.get('seconds', 0)
            )
        else:
            raise JobConfigException(
                f"Invalid trigger ({trigger}) when scheduling job with id: {job_id}"
            )

        self.scheduler.add_job(
            job_function,
            trigger=job_trigger,
            id=job_id,
            replace_existing=replace
        )

    def shutdown_jobs(self):
        logger.info("Shutting down scheduled jobs")
        self.scheduler.shutdown()
