# pyrefly: ignore [missing-import]
import uvicorn
from app.main import app

if __name__ == "__main__":
    # Start uvicorn server mapping to our modular app setup
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
