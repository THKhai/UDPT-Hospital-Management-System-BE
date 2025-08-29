from contextlib import asynccontextmanager
from dependency_injector import containers, providers
from src.core.container import Container
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.controllers.user_controller import router as user_router
from config.settings import settings
from config.database import test_db_connection, init_db
from src.controllers .login_controller import login_router
from config.database_utils import (
    get_database_info,
    diagnose_database_issues
)
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app with settings
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info(f"Starting {settings.app.title} v{settings.app.version}")
    logger.info(f"Database URL: {settings.database.url}")
    logger.info(f"Debug mode: {settings.app.debug}")

    try:
        if test_db_connection():
            logger.info("Database connection successful")
            init_db()
            logger.info("Database tables initialized")
            db_info = get_database_info()
            logger.info(f"Database: {db_info.get('driver', 'unknown')} - {db_info.get('status', 'unknown')}")
        else:
            logger.error("Database connection failed - check your database configuration")
            db_diagnosis = diagnose_database_issues()
            logger.error(f"Database diagnosis: {db_diagnosis}")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't stop the application, but log the error

    yield

    # Shutdown logic
    logger.info("Shutting down application")


container = Container()
container.wire(modules=[
    "src.controllers.login_controller"
])
app = FastAPI(
    title=settings.app.title,
    description=settings.app.description,
    version=settings.app.version,
    debug=settings.app.debug,
    lifespan=lifespan
)
# Add this configuration
app.swagger_ui_init_oauth = {
    "usePkceWithAuthorizationCodeGrant": True,
    "clientId": "",
    "clientSecret": ""
}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router)
app.include_router(login_router)
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app.title}",
        "version": settings.app.version,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check with database diagnostics"""
    db_status = "healthy" if test_db_connection() else "unhealthy"

    health_data = {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.app.version,
        "database": db_status,
        "message": "Service is running"
    }

    # Add detailed database info if available
    try:
        db_info = get_database_info()

        health_data["database_details"] = {
            "driver": db_info.get("driver"),
            "pool_size": settings.database.pool_size,
            "schema": "admin"
        }
    except Exception as e:
        health_data["database_error"] = str(e)

    return health_data

@app.get("/diagnosis")
async def database_diagnosis():
    """Detailed database diagnosis endpoint"""
    return diagnose_database_issues()