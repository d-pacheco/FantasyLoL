import uvicorn

from src.fantasy import app
from src.common.logger import configure_logger

if __name__ == "__main__":
    configure_logger()
    uvicorn.run(app, host="0.0.0.0", port=80)
