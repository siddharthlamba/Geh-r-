import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import engine, Base, SessionLocal
from .models import User, Department, Complaint, ComplaintEvent, ChatSession, ChatMessage
from .seed_data import seed_database
from .routers import agent_router, complaints, dashboard, settings_router, uploads

# Ensure database tables exist and seed demo data on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB & run safe migrations
    from .database import run_migrations
    run_migrations()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title="Gehor - AI Complaint Management Platform API",
    description="Conversational complaint registration, classification, routing, and tracking API.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for local development & frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads static folder
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Include API Routers
app.include_router(agent_router.router)
app.include_router(complaints.router)
app.include_router(dashboard.router)
app.include_router(settings_router.router)
app.include_router(uploads.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Gehor Core API",
        "version": "1.0.0"
    }

# Mount React static build if present
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # SPA catch-all for frontend routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Exclude /api routes
        if full_path.startswith("api/") or full_path.startswith("uploads/"):
            return {"error": "Not Found"}
        target_file = os.path.join(frontend_dist, full_path)
        if os.path.exists(target_file) and os.path.isfile(target_file):
            return FileResponse(target_file)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
