"""
Annuaire Contacts API - Main application
"""

from fastapi import FastAPI
from database import init_db
from routes import register_all_routes
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Annuaire Contacts API", version="0.1.0")


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
