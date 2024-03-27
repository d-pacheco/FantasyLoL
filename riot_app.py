import uvicorn

from src.common.logger import configure_logger
from src.riot import app
from src.riot.util.job_scheduler import JobScheduler

if __name__ == "__main__":
    configure_logger()
    job_scheduler = JobScheduler()
    job_scheduler.schedule_all_jobs()
    uvicorn.run(app, host="0.0.0.0", port=80)
