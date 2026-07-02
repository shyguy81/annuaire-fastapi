"""
Annuaire Contacts API - Main application
"""

from fastapi import FastAPI
from database import init_db
from routes import register_all_routes
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Swagger UI tags and structure
tags_metadata = [
    {
        "name": "Contacts",
        "description": "CRUD operations for managing contacts (create, read, update, delete, search)"
    },
    {
        "name": "Relationship Profiles",
        "description": "Manage relationship profiles for contacts (trust level, proximity, business potential)"
    },
    {
        "name": "Actions",
        "description": "Create and track relationship actions (tasks/reminders with status and priority)"
    },
    {
        "name": "Interactions",
        "description": "Record and track interactions with contacts (calls, emails, meetings, etc.)"
    },
    {
        "name": "Dashboard",
        "description": "System-wide RAP metrics and aggregated statistics"
    }
]

app = FastAPI(
    title="Annuaire Contacts API",
    version="0.0.8",
    openapi_tags=tags_metadata,
    swagger_ui_parameters={"docExpansion": "list"}  # Collapse sections by default
)


@app.on_event("startup")
def startup():
    """Initialize database on startup"""
    init_db()
    logger.info("Database initialized")


@app.get("/health")
def health():
    """Health check"""
    return {"status": "ok"}


# Register all route modules
register_all_routes(app)
