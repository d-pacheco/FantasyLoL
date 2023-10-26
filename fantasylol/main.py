from fastapi import FastAPI

from api import router as api_router
from db.database import engine
from db import models
from util.JobScheduler import JobScheduler

app = FastAPI()
app.include_router(api_router)
models.Base.metadata.create_all(bind=engine)

job_scheduler = JobScheduler()
job_scheduler.schedule_all_jobs()

@app.get("/")
def home():
    return {"Data": "Test"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)