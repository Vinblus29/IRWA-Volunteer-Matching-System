import motor.motor_asyncio
from typing import Optional
import logging
from .config import settings

logger = logging.getLogger(__name__)

class Database:
    client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
    database: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        db.client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.mongodb_url,
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=45000,
            waitQueueTimeoutMS=5000
        )
        
        # Test the connection
        await db.client.admin.command('ping')
        db.database = db.client[settings.database_name]
        
        # Create indexes
        await create_indexes()
        
        logger.info("Successfully connected to MongoDB")
        
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Users collection indexes
        await db.database.users.create_index("email", unique=True)
        await db.database.users.create_index("username", unique=True)
        
        # Volunteers collection indexes
        await db.database.volunteers.create_index("user_id", unique=True)
        await db.database.volunteers.create_index([("skills.name", 1)])
        await db.database.volunteers.create_index([("location.coordinates", "2dsphere")])
        await db.database.volunteers.create_index("availability.day")
        
        # Events collection indexes
        await db.database.events.create_index("organization_id")
        await db.database.events.create_index("date")
        await db.database.events.create_index([("location.coordinates", "2dsphere")])
        await db.database.events.create_index([("required_skills.name", 1)])
        await db.database.events.create_index("status")
        
        # Matches collection indexes
        await db.database.matches.create_index("volunteer_id")
        await db.database.matches.create_index("event_id")
        await db.database.matches.create_index("match_score")
        await db.database.matches.create_index("created_at")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

def get_database():
    """Get database instance"""
    return db.database 