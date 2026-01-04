"""
Database seeding script for populating PostgreSQL tables from CSV files.
"""
import os
import sys
import csv
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from contextlib import contextmanager
import logging
from models import Department, Perimeter, ACL

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


# Global database instance
db = DatabaseConnection()

class CSVLoader:
    """Handles loading and parsing CSV files into memory."""
    
    def __init__(self, data_dir: str = "."):
        """
        Initialize CSV loader.
        
        Args:
            data_dir: Directory containing CSV files (default: current directory)
        """
        self.data_dir = data_dir
        logger.info(f"CSV Loader initialized with data directory: {data_dir}")
    
    def load_departments(self) -> List[Dict[str, Any]]:
        """
        Load departments from CSV file.
        
        Returns:
            List of department dictionaries with keys: id, name
            
        Raises:
            FileNotFoundError: If departments.csv not found
            ValueError: If CSV format is invalid
        """
        filepath = os.path.join(self.data_dir, "departments.csv")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"departments.csv not found at {filepath}")
        
        departments = []
        
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                if not reader.fieldnames or set(reader.fieldnames) != {'ID', 'Name'}:
                    raise ValueError(
                        f"Invalid departments.csv headers. Expected ['ID', 'Name'], "
                        f"got {reader.fieldnames}"
                    )
                
                for row in reader:
                    try:
                        department = {
                            'id': float(row['ID']),
                            'name': row['Name'].strip()
                        }
                        departments.append(department)
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Skipping invalid department row: {row} - {e}")
                        continue
            
            logger.info(f"✓ Loaded {len(departments)} departments from CSV")
            return departments
            
        except Exception as e:
            logger.error(f"✗ Failed to load departments.csv: {e}")
            raise
    
    def load_perimeters(self) -> List[Dict[str, Any]]:
        """
        Load perimeters from CSV file.
        
        Returns:
            List of perimeter dictionaries with keys: id, name, department_id
            
        Raises:
            FileNotFoundError: If perimeters.csv not found
            ValueError: If CSV format is invalid
        """
        filepath = os.path.join(self.data_dir, "perimeters.csv")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"perimeters.csv not found at {filepath}")
        
        perimeters = []
        
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                expected_headers = {'Id', 'PerimeterName', 'BU_Id', 'BU_Name'}
                if not reader.fieldnames or set(reader.fieldnames) != expected_headers:
                    raise ValueError(
                        f"Invalid perimeters.csv headers. Expected {expected_headers}, "
                        f"got {set(reader.fieldnames) if reader.fieldnames else 'None'}"
                    )
                
                for row in reader:
                    try:
                        perimeter = {
                            'id': int(row['Id']),
                            'name': row['PerimeterName'].strip(),
                            'department_id': float(row['BU_Id'])
                        }
                        perimeters.append(perimeter)
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Skipping invalid perimeter row: {row} - {e}")
                        continue
            
            logger.info(f"✓ Loaded {len(perimeters)} perimeters from CSV")
            return perimeters
            
        except Exception as e:
            logger.error(f"✗ Failed to load perimeters.csv: {e}")
            raise
    
    def load_acls(self) -> List[Dict[str, Any]]:
        """
        Load ACLs from CSV file.
        
        Returns:
            List of ACL dictionaries with keys: user, access_level, id
            
        Raises:
            FileNotFoundError: If acl.csv not found
            ValueError: If CSV format is invalid
        """
        filepath = os.path.join(self.data_dir, "acl.csv")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"acl.csv not found at {filepath}")
        
        acls = []
        
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                expected_headers = {'User', 'AccessLevel', 'Id'}
                if not reader.fieldnames or set(reader.fieldnames) != expected_headers:
                    raise ValueError(
                        f"Invalid acl.csv headers. Expected {expected_headers}, "
                        f"got {set(reader.fieldnames) if reader.fieldnames else 'None'}"
                    )
                
                for row in reader:
                    try:
                        acl = {
                            'user': row['User'].strip(),
                            'access_level': row['AccessLevel'].strip(),
                            'id': float(row['Id'])
                        }
                        acls.append(acl)
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Skipping invalid ACL row: {row} - {e}")
                        continue
            
            logger.info(f"✓ Loaded {len(acls)} ACLs from CSV")
            return acls
            
        except Exception as e:
            logger.error(f"✗ Failed to load acl.csv: {e}")
            raise
    
    def load_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load all CSV files in dependency order.
        
        Returns:
            Dictionary with keys: departments, perimeters, acls
        """
        return {
            'departments': self.load_departments(),
            'perimeters': self.load_perimeters(),
            'acls': self.load_acls()
        }


class TransactionManager:
    """Manages database transactions and data insertion."""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Initialize transaction manager.
        
        Args:
            db_connection: DatabaseConnection instance
        """
        self.db = db_connection
        self.inserted_counts = {
            'departments': 0,
            'perimeters': 0,
            'acls': 0
        }
    
    def insert_departments(self, departments: List[Dict[str, Any]]) -> int:
        """
        Insert departments into database.
        
        Args:
            departments: List of department dictionaries
            
        Returns:
            Number of departments inserted
            
        Raises:
            Exception: If insertion fails
        """
        inserted = 0
        skipped = 0
        
        try:
            with self.db.session_scope() as session:
                for dept in departments:
                    try:
                        # Check if department already exists
                        existing = session.query(Department).filter_by(id=dept['id']).first()
                        
                        if existing:
                            logger.debug(f"Skipping duplicate department ID: {dept['id']}")
                            skipped += 1
                            continue
                        
                        # Create new department
                        department = Department(
                            id=dept['id'],
                            name=dept['name']
                        )
                        
                        session.add(department)
                        inserted += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to insert department {dept}: {e}")
                        skipped += 1
                        continue
            
            self.inserted_counts['departments'] = inserted
            logger.info(f"✓ Inserted {inserted} departments ({skipped} skipped)")
            return inserted
            
        except Exception as e:
            logger.error(f"✗ Transaction failed for departments: {e}")
            raise
    
    def insert_perimeters(self, perimeters: List[Dict[str, Any]]) -> int:
        """
        Insert perimeters into database.
        
        Args:
            perimeters: List of perimeter dictionaries
            
        Returns:
            Number of perimeters inserted
        """
        # TODO: Implement perimeter insertion
        logger.info("Perimeter insertion not yet implemented")
        return 0
    
    def insert_acls(self, acls: List[Dict[str, Any]]) -> int:
        """
        Insert ACLs into database.
        
        Args:
            acls: List of ACL dictionaries
            
        Returns:
            Number of ACLs inserted
        """
        # TODO: Implement ACL insertion
        logger.info("ACL insertion not yet implemented")
        return 0
    
    def get_summary(self) -> str:
        """
        Get summary of inserted records.
        
        Returns:
            Summary string
        """
        return (
            f"Insertion Summary:\n"
            f"  Departments: {self.inserted_counts['departments']}\n"
            f"  Perimeters:  {self.inserted_counts['perimeters']}\n"
            f"  ACLs:        {self.inserted_counts['acls']}"
        )


def main():
    """Main entry point."""
    try:
        # Connect to database
        db.connect()
        
        logger.info("Database connection ready for seeding")

        csvHelper = CSVLoader(data_dir="data")
        data = csvHelper.load_all()

        transactionManager = TransactionManager(db)
        transactionManager.insert_departments(data['departments'])

        logger.info("Loaded CSV data for keys: %s", data.keys())
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        db.disconnect()


if __name__ == "__main__":
    main()
