# app/db.py — MongoDB connection
import os
import logging
from pymongo import MongoClient

logger = logging.getLogger(__name__)

db = None
mongo_client = None

try:
    MONGO_URI = os.environ.get('MONGO_URI')
    if MONGO_URI:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        mongo_client.admin.command('ping')  # Test connection
        db = mongo_client['AI_interview']
        logger.info("MongoDB connected successfully.")
    else:
        logger.error("MONGO_URI not set in .env — MongoDB disabled.")
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")
    db = None
    mongo_client = None
