# app/main.py

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# dependencies
from app.routers.scan_router import ensure_test_user
from app.dependencies import get_db

# import routers by name
from app.routers.auth import router as auth_router
from app.routers.scan_router import router as scan_router
from app.routers.dashboard import router as dashboard_router
from app.routers.org_router import router as org_router

# configure logging to show debug-level messages
logging.basicConfig(level=logging.DEBUG)

app = FastAPI(
    title="Shield Scan Vulnerability Management API",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url=None,
    debug=True,
)

# simple health check
@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# seed test user on startup
@app.on_event("startup")
async def seed_test_user():
    print("🔄 Seeding test user…")
    db_gen = get_db()
    db = next(db_gen)
    try:
        await ensure_test_user(db)
        print("✅ Test user ready")
    finally:
        db.close()

# custom OpenAPI to include bearerAuth
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    schema.setdefault("components", {})\
          .setdefault("securitySchemes", {})["bearerAuth"] = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi

# mount routers under /api/v1
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(scan_router, prefix="/api/v1", tags=["scan"])
app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])
app.include_router(org_router, prefix="/api/v1", tags=["organizations"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


# uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

