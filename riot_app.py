import uvicorn
import sys

from src.common.logger import configure_logger
from src.riot import app
from src.riot.util.job_scheduler import JobScheduler


if __name__ == "__main__":
    try:
        configure_logger()
        job_scheduler = JobScheduler()
        #job_scheduler.schedule_all_jobs()
        uvicorn.run(app, host="0.0.0.0", port=80)
    except KeyboardInterrupt:
        print("Exiting")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
