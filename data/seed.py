"""
Database seeding script for populating PostgreSQL tables from CSV files.
"""
import os
import sys
from sqlalchemy import create_engine, event, text
from csv_loader import CSVLoader
from database_connection import DatabaseConnection
from transaction_manager import TransactionManager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    try:
        # Global database instance
        db = DatabaseConnection()

        # Connect to database
        db.connect()
        
        logger.info("Database connection ready for seeding")

        csvHelper = CSVLoader(data_dir="files")
        data = csvHelper.load_all()
        logger.info("Loaded CSV data for keys: %s", data.keys())

        transactionManager = TransactionManager(db)
        transactionManager.insert_departments(data['departments'])
        transactionManager.insert_perimeters(data['perimeters'])
        transactionManager.insert_acls(data['acls'])        
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        db.disconnect()


if __name__ == "__main__":
    main()
