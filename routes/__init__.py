"""
Routes module - aggregates all route registrations
"""

from fastapi import FastAPI
from .contacts import register_contact_routes
from .relationship_profiles import register_relationship_profile_routes
from .interactions import register_interaction_routes
from .actions import register_action_routes


def register_all_routes(app: FastAPI):
    """Register all routes with the FastAPI app"""
    register_contact_routes(app)
    register_relationship_profile_routes(app)
    register_interaction_routes(app)
    register_action_routes(app)
