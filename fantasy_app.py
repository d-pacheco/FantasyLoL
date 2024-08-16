import uvicorn
import sys
from src.fantasy import app
from src.common.logger import configure_logger

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
