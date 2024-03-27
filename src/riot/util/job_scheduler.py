import logging
import atexit
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from src.riot.exceptions.JobConfigException import JobConfigException
from src.riot.service.riot_league_service import RiotLeagueService
from src.riot.service.riot_tournament_service import RiotTournamentService
from src.riot.service.riot_professional_team_service import RiotProfessionalTeamService
from src.riot.service.riot_professional_player_service import RiotProfessionalPlayerService
from src.riot.service.riot_match_service import RiotMatchService
from src.riot.service.riot_game_service import RiotGameService
from src.riot.service.riot_game_stats_service import RiotGameStatsService
from src.common.config import Config

logger = logging.getLogger('fantasy-lol')


class JobScheduler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JobScheduler, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.riot_league_service = RiotLeagueService()
        self.riot_tournament_service = RiotTournamentService()
        self.riot_team_service = RiotProfessionalTeamService()
        self.riot_player_service = RiotProfessionalPlayerService()
        self.riot_match_service = RiotMatchService()
        self.riot_game_service = RiotGameService()
        self.riot_game_stats_service = RiotGameStatsService()

        job_store = SQLAlchemyJobStore(url=Config.DATABASE_URL)
        self.scheduler = BackgroundScheduler(jobstores={'default': job_store})
        self.scheduler.start()
        atexit.register(self.shutdown_jobs)

    def __init__(self):
        pass

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
            job_config=Config.LEAGUE_SERVICE_SCHEDULE,
            job_id='league_service_job',
        )
        self.schedule_job(
            job_function=self.riot_tournament_service.fetch_tournaments_retry_job,
            job_config=Config.TOURNAMENT_SERVICE_SCHEDULE,
            job_id='tournament_service_job'
        )
        self.schedule_job(
            job_function=self.riot_team_service.fetch_professional_teams_from_riot_retry_job,
            job_config=Config.TEAM_SERVICE_SCHEDULE,
            job_id='team_service_job'
        )
        self.schedule_job(
            job_function=self.riot_player_service.fetch_professional_players_from_riot_retry_job,
            job_config=Config.PLAYER_SERVICE_SCHEDULE,
            job_id='player_service_job'
        )
        self.schedule_job(
            job_function=self.riot_match_service.fetch_new_schedule_retry_job,
            job_config=Config.MATCH_SERVICE_SCHEDULE,
            job_id='match_service_job'
        )
        self.schedule_job(
            job_function=self.riot_game_service.fetch_games_from_match_ids_retry_job,
            job_config=Config.GAME_SERVICE_SCHEDULE,
            job_id='games_from_match_ids_job'
        )
        self.schedule_job(
            job_function=self.riot_game_service.update_game_states_retry_job,
            job_config=Config.GAME_SERVICE_SCHEDULE,
            job_id='update_game_states_job'
        )
        self.schedule_job(
            job_function=self.riot_game_stats_service.run_player_metadata_retry_job,
            job_config=Config.GAME_STATS_SERVICE_SCHEDULE,
            job_id='player_metadata_job'
        )
        self.schedule_job(
            job_function=self.riot_game_stats_service.run_player_stats_retry_job,
            job_config=Config.GAME_STATS_SERVICE_SCHEDULE,
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
