from fastapi import FastAPI

from app.core.error_handlers import register_error_handlers
from app.routers import admin, auth, barangays, me

API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    app = FastAPI(title="UGNAY API", version="0.1.0")
    register_error_handlers(app)
    for router in (auth.router, me.router, barangays.router, admin.router):
        app.include_router(router, prefix=API_PREFIX)
    return app


app = create_app()
