import logging
from typing import List, Dict, Any, Optional
from database_connection import DatabaseConnection
from models import Department, Perimeter, ACL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
        try:
            inserted = 0
            skipped = 0

            with self.db.session_scope() as session:
                for perm in perimeters:
                    try:
                        # Check if perimeter already exists
                        perimeter = session.query(Perimeter).filter_by(name=perm['name']).first()
                        
                        if perimeter:
                            logger.debug(f"Skipping duplicate perimeter ID: {perm['id']}")
                            skipped += 1                            
                        else:
                            # Create new perimeter
                            perimeter = Perimeter(
                                id=perm['id'],
                                name=perm['name']                            
                            )                        

                    
                        # Handle perimeter-department association (one per perimeter)
                        dept_id = perm['department_id']
                        if dept_id:
                            department = session.query(Department).filter_by(id=dept_id).first()
                            if department:
                                perimeter.departments.append(department)
                            else:
                                logger.warning(f"Department (department_id) {dept_id} not found for perimeter {perm['id']}")
                        else:
                            logger.warning(f"No department_id found for perimeter {perm['id']}")
                        
                        session.add(perimeter)
                        inserted += 1

                    except Exception as e:
                        logger.warning(f"Failed to insert perimeter {perm}: {e}")
                        skipped += 1
                        continue
            
            self.inserted_counts['perimeters'] = inserted
            logger.info(f"✓ Inserted {inserted} perimeters ({skipped} skipped )")
            return inserted

        except Exception as e:
            logger.error(f"✗ Transaction failed for perimeters: {e}")
            raise
    
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