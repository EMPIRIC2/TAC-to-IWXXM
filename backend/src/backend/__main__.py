"""Entry point for running backend standalone with `python -m backend`."""
from fastapi import FastAPI
from .api import app as backend_app

app = backend_app  # expose existing FastAPI instance

__all__ = ["app"]