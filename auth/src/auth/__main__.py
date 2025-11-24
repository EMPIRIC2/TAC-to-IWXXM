"""Entry point for running the auth service via `python -m auth`."""
from fastapi import FastAPI
from pydantic import BaseModel
from .api import router


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


app = FastAPI(title="METAR Auth Service", version="0.1.0")
app.include_router(router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health check endpoint for Docker."""
    return HealthResponse(status="healthy", service="auth", version="0.1.0")


__all__ = ["app"]
