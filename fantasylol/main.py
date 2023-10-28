from fastapi import FastAPI
import uvicorn

from api import router as api_router
from db.database import engine
from db import models
from util.JobScheduler import JobScheduler

app = FastAPI()
app.include_router(api_router)
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"Data": "Test"}

if __name__ == "__main__":
    job_scheduler = JobScheduler()
    job_scheduler.schedule_all_jobs()
    uvicorn.run(app, host="0.0.0.0", port=8000)