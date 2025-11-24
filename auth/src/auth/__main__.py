"""Entry point for running the auth service via `python -m auth`."""
from fastapi import FastAPI
from .api import router

app = FastAPI()
app.include_router(router)

__all__ = ["app"]
