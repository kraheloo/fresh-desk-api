import csv
import os
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
                            'access_level': 'P' if row['AccessLevel'].strip() == 'Perimeter' else 'D',
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