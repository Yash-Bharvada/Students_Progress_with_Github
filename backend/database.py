"""
MongoDB database connection and management using Motor async driver.
Handles async connection management and provides collection accessors.
"""

import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from backend.config import get_settings


class Database:
    """
    Async MongoDB database connection manager.
    Provides connection lifecycle management and collection accessors.
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """Initialize database connection manager."""
        self.connection_string = connection_string or get_settings().mongodb_connection_string
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self._is_connected = False
    
    async def connect(self) -> None:
        """
        Establish async connection to MongoDB.
        Raises ConnectionError if connection fails.
        """
        try:
            print(f"🔌 Connecting to MongoDB...")
            
            # Create Motor client with connection options
            self.client = AsyncIOMotorClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,         # 10 second connection timeout
                maxPoolSize=10,                 # Connection pool size
                retryWrites=True
            )
            
            # Extract database name from connection string
            db_name = self._extract_database_name()
            self.db = self.client[db_name]
            
            # Test the connection
            await self.client.admin.command('ping')
            self._is_connected = True
            
            print(f"✅ Successfully connected to MongoDB database: {db_name}")
            
            # Create indexes for optimal performance
            await self._create_indexes()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            error_msg = f"Failed to connect to MongoDB: {str(e)}"
            print(f"❌ {error_msg}")
            raise ConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error connecting to MongoDB: {str(e)}"
            print(f"❌ {error_msg}")
            raise ConnectionError(error_msg) from e
    
    async def disconnect(self) -> None:
        """Close the database connection."""
        if self.client:
            print("🔌 Disconnecting from MongoDB...")
            self.client.close()
            self.client = None
            self.db = None
            self._is_connected = False
            print("✅ Disconnected from MongoDB")
    
    def _extract_database_name(self) -> str:
        """Extract database name from MongoDB connection string."""
        try:
            # Handle both mongodb:// and mongodb+srv:// formats
            if '/' in self.connection_string:
                # Extract database name after the last '/' and before '?'
                db_part = self.connection_string.split('/')[-1]
                db_name = db_part.split('?')[0]
                if db_name:
                    return db_name
            
            # Default database name if not specified in connection string
            return "student_progress"
            
        except Exception:
            return "student_progress"
    
    async def _create_indexes(self) -> None:
        """Create database indexes for optimal performance."""
        try:
            print("📊 Creating database indexes...")
            
            # User collection indexes
            await self.users.create_index("githubId", unique=True)
            await self.users.create_index("role")
            await self.users.create_index("enrolledBy")
            
            # Repository collection indexes
            await self.repositories.create_index("ownerGithubId")
            await self.repositories.create_index("repoUrl", unique=True)
            await self.repositories.create_index("linkedStudents")
            
            # ContributionMetrics collection indexes
            await self.contribution_metrics.create_index([("repoId", 1), ("studentGithubId", 1)], unique=True)
            await self.contribution_metrics.create_index("studentGithubId")
            await self.contribution_metrics.create_index("repoId")
            
            # AIFeedback collection indexes
            await self.ai_feedback.create_index([("repoId", 1), ("studentGithubId", 1)])
            await self.ai_feedback.create_index("studentGithubId")
            await self.ai_feedback.create_index("generatedAt")
            
            print("✅ Database indexes created successfully")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not create indexes: {str(e)}")
            # Don't raise error for index creation failures
    
    def _ensure_connected(self) -> None:
        """Ensure database is connected before operations."""
        if not self._is_connected or self.db is None:
            raise ConnectionError("Database not connected. Call connect() first.")
    
    @property
    def users(self) -> AsyncIOMotorCollection:
        """Get users collection."""
        self._ensure_connected()
        return self.db.users
    
    @property
    def repositories(self) -> AsyncIOMotorCollection:
        """Get repositories collection."""
        self._ensure_connected()
        return self.db.repositories
    
    @property
    def contribution_metrics(self) -> AsyncIOMotorCollection:
        """Get contribution_metrics collection."""
        self._ensure_connected()
        return self.db.contribution_metrics
    
    @property
    def ai_feedback(self) -> AsyncIOMotorCollection:
        """Get ai_feedback collection."""
        self._ensure_connected()
        return self.db.ai_feedback
    
    async def health_check(self) -> dict:
        """
        Perform database health check.
        Returns status information about the database connection.
        """
        try:
            self._ensure_connected()
            
            # Ping the database
            ping_result = await self.client.admin.command('ping')
            
            # Get server info
            server_info = await self.client.server_info()
            
            # Count documents in collections
            user_count = await self.users.count_documents({})
            repo_count = await self.repositories.count_documents({})
            metrics_count = await self.contribution_metrics.count_documents({})
            feedback_count = await self.ai_feedback.count_documents({})
            
            return {
                "status": "healthy",
                "connected": True,
                "database_name": self.db.name,
                "server_version": server_info.get("version", "unknown"),
                "collections": {
                    "users": user_count,
                    "repositories": repo_count,
                    "contribution_metrics": metrics_count,
                    "ai_feedback": feedback_count
                },
                "ping": ping_result
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }


# Global database instance
db: Optional[Database] = None


def get_database() -> Database:
    """Get database singleton instance."""
    global db
    if db is None:
        db = Database()
    return db


async def connect_database() -> Database:
    """Connect to database and return instance."""
    database = get_database()
    if not database._is_connected:
        await database.connect()
    return database


async def disconnect_database() -> None:
    """Disconnect from database."""
    global db
    if db and db._is_connected:
        await db.disconnect()


# Context manager for database operations
class DatabaseManager:
    """Context manager for database operations."""
    
    def __init__(self):
        self.database = None
    
    async def __aenter__(self) -> Database:
        """Enter async context and connect to database."""
        self.database = await connect_database()
        return self.database
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context (keep connection alive for reuse)."""
        # Don't disconnect here - let the application manage connection lifecycle
        pass


if __name__ == "__main__":
    # Test database connection
    async def test_connection():
        try:
            async with DatabaseManager() as database:
                health = await database.health_check()
                print(f"Database health check: {health}")
        except Exception as e:
            print(f"Database test failed: {e}")
    
    asyncio.run(test_connection())