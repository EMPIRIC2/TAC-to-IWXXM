"""Standalone launch for auth service (optional).

Run: python -m auth
"""
from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from . import router, init_db

app = FastAPI(title="Auth Service", version="0.1.0")
app.include_router(router)


@app.on_event("startup")
def _startup():  # pragma: no cover
    init_db()


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run("auth.__main__:app", host="0.0.0.0", port=8100, reload=False)
