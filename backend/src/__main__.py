"""Entry point for running backend with `python -m src` or from the backend package."""
import os
import sys

if __name__ == "__main__":
    import uvicorn
    from .api import app

    # Get configuration from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8001"))
    reload = os.getenv("RELOAD", "true").lower() in ("true", "1", "yes")

    print("🚀 Starting METAR to IWXXM Backend API...")
    print(f"📡 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://localhost:{port}/docs")
    print(f"📖 ReDoc: http://localhost:{port}/redoc")
    print(f"💚 Health: http://localhost:{port}/health")
    print("")
    print("Press CTRL+C to stop the server")
    print("")

    uvicorn.run(
        "src.api:app",
        host=host,
        port=port,
        reload=reload,
    )
