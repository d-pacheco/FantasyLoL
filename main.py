import uvicorn
from fantasylol import app
from fantasylol.util.JobScheduler import JobScheduler


if __name__ == "__main__":
    #job_scheduler = JobScheduler()
    #job_scheduler.schedule_all_jobs()
    uvicorn.run(app, host="0.0.0.0", port=8000)
