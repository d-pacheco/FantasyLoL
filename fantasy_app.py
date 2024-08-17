import uvicorn
import sys
from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from src.fantasy.endpoints import router
from src.common.logger import configure_logger


app = FastAPI()
add_pagination(app)
disable_installed_extensions_check()
app.include_router(router)

if __name__ == "__main__":
    try:
        configure_logger()
        uvicorn.run(app, host="0.0.0.0", port=80)
    except KeyboardInterrupt:
        print("Exiting")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
