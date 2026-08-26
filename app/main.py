from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.connection import init_db, SessionLocal
from app.database.seed import seed_initial_admin
from app.auth.routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events lifecycle manager.
    Initializes database tables and seeds default admin user on application launch.
    """
    # Startup actions
    init_db()
    db = SessionLocal()
    try:
        seed_initial_admin(db)
    finally:
        db.close()
    
    yield

    # Shutdown actions (if any)


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Blood Bank Management System - Authentication, Authorization & Database Foundation API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Frontend Integration (Member 2)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Auth Router
app.include_router(auth_router)


@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs_url": "/docs"
    }
