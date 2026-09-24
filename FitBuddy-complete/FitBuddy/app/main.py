from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import create_tables
from .routes import router

settings = get_settings()

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title=settings.app_name,
    description="AI-powered personalized 7-day fitness plan generator.",
    version="1.0.0",
    debug=settings.debug,
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(router)


@app.on_event("startup")
def startup() -> None:
    create_tables()
