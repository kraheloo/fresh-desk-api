import os
import sys
import logging
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Manages database connection and session lifecycle."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            database_url: PostgreSQL connection string. 
                         If None, uses DATABASE_URL env var or default.
        """
        self.database_url = database_url or self._get_database_url()
        self.engine: Optional[Engine] = None
        self.SessionLocal = None
        
        logger.info(f"Initializing database connection to: {self._mask_url(self.database_url)}")
    
    @staticmethod
    def _get_database_url() -> str:
        """
        Get database URL from environment or use default.
        
        Returns:
            Database connection URL
            
        Raises:
            ValueError: If no database URL is available
        """
        url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:Protocol_101!@localhost/freshdesk"
        )
        
        if not url:
            raise ValueError(
                "DATABASE_URL environment variable not set and no default available. "
                "Please set DATABASE_URL or provide database_url parameter."
            )
        
        return url
    
    @staticmethod
    def _mask_url(url: str) -> str:
        """Mask password in database URL for logging."""
        if "@" in url:
            scheme, rest = url.split("://", 1)
            if ":" in rest.split("@")[0]:
                user_pass, host = rest.split("@", 1)
                user = user_pass.split(":")[0]
                return f"{scheme}://{user}:***@{host}"
        return url
    
    def connect(self) -> None:
        """
        Establish database connection and create session factory.
        
        Raises:
            Exception: If connection fails
        """
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                self.database_url,
                echo=False,  # Set to True for SQL debugging
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Test connections before using
            )
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✓ Database connection successful")
            
            # Create session factory
            self.SessionLocal = sessionmaker(bind=self.engine)
            
        except Exception as e:
            logger.error(f"✗ Failed to connect to database: {e}")
            raise
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            SQLAlchemy session object
            
        Raises:
            RuntimeError: If not connected
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self):
        """
        Context manager for database sessions with automatic cleanup.
        
        Usage:
            with db.session_scope() as session:
                session.query(...).all()
        
        Yields:
            SQLAlchemy session object
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
            logger.debug("✓ Transaction committed")
        except Exception as e:
            session.rollback()
            logger.error(f"✗ Transaction rolled back: {e}")
            raise
        finally:
            session.close()
    
    def disconnect(self) -> None:
        """Close all database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("✓ Database connection closed")