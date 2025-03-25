"""Database utilities for resetting and recreating the database."""

import logging
import os
from flask import current_app

logger = logging.getLogger(__name__)

def reset_database(app, db):
    """Drops all tables and recreates them"""
    with app.app_context():
        logger.info("Resetting database...")
        try:
            db.drop_all()
            logger.info("All tables dropped successfully")
            db.create_all()
            logger.info("All tables created successfully")
            
            # Import and call populate_db
            from .init_db import populate_db
            populate_db(app)
            logger.info("Database populated successfully")
            
            return True
        except Exception as e:
            logger.error(f"Error resetting database: {str(e)}")
            return False 