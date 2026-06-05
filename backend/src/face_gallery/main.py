import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from face_gallery.api.routes import health, jobs, libraries, persons, thumbs
from face_gallery.config import get_settings
from face_gallery.db.connection import init_db
from face_gallery.ml.model_setup import ensure_models
from face_gallery.services.queue_worker import (
    reset_stuck_jobs_on_startup,
    start_queue_worker,
    stop_queue_worker,
)

_shutdown_requested = False


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger("face_gallery").setLevel(logging.INFO)
    settings = get_settings()
    settings.resolve_paths()
    ensure_models()
    init_db()
    n = reset_stuck_jobs_on_startup()
    if n:
        logging.getLogger(__name__).info("Re-queued %s stuck scan job(s) on startup", n)
    start_queue_worker()
    yield
    stop_queue_worker()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Face Gallery API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(libraries.router)
    app.include_router(jobs.router)
    app.include_router(persons.router)
    app.include_router(thumbs.router)

    @app.post("/shutdown")
    def shutdown() -> dict[str, str]:
        global _shutdown_requested
        _shutdown_requested = True

        def _exit() -> None:
            os._exit(0)

        import threading

        threading.Timer(0.3, _exit).start()
        return {"status": "shutting_down"}

    return app


app = create_app()


def _run_test_detect(image_arg: str) -> int:
    from pathlib import Path

    from face_gallery.ml.model_setup import ensure_models
    from face_gallery.services.embedder import detect_faces

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ensure_models()
    path = Path(image_arg)
    try:
        faces, w, h = detect_faces(path)
        print(f"OK faces={len(faces)} size={w}x{h}")
        return 0
    except Exception as exc:
        print(f"FAIL {type(exc).__name__}: {exc}")
        import traceback

        traceback.print_exc()
        return 1


def main() -> None:
    import uvicorn

    if "--test-detect" in sys.argv:
        idx = sys.argv.index("--test-detect")
        if idx + 1 >= len(sys.argv):
            print("Usage: api --test-detect <image-path>")
            raise SystemExit(2)
        raise SystemExit(_run_test_detect(sys.argv[idx + 1]))

    settings = get_settings()
    port = settings.api_port
    if "--port" in sys.argv:
        i = sys.argv.index("--port")
        port = int(sys.argv[i + 1])
    uvicorn.run(
        app,
        host=settings.api_host,
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
