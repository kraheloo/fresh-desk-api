# FreshService API Integration Scripts

A collection of Python scripts for interacting with the FreshService API to retrieve and analyze incident and service request data with organizational access control.

## Overview

This repository contains scripts to:
- Retrieve recent open incidents and service requests
- Generate incident count reports with date filtering
- Implement CSV-based access control for organizational hierarchy
- Filter data by department and perimeter access levels

## Prerequisites

- Python 3.7+
- Required packages: `requests`

Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The scripts use the following configuration:
- **API Instance**: `axiansnetworkltd.freshservice.com`
- **API Key**: Configured in each script (consider using environment variables for production)

## CSV Data Structure

The system uses three CSV files in the `data/` directory:

### 1. `departments.csv`
Stores all FreshService departments with their IDs.

**Format:**
```csv
ID,Name
54000211461,"DESKTOP 2026 AXIANS BASINGSTOKE"
54000211463,"DESKTOP 2026 AXIANS COVENTRY"
```

### 2. `perimeters.csv`
Creates virtual groupings (perimeters) containing multiple departments.

**Format:**
```csv
Id,PerimeterName,BU_Id,BU_Name
1,Axians,54000211461,"DESKTOP 2026 AXIANS BASINGSTOKE"
1,Axians,54000211463,"DESKTOP 2026 AXIANS COVENTRY"
2,Actemium Automation,54000211448,"DESKTOP 2026 ACTEMIUM AUTO HAMPSHIRE"
```

- `Id`: Numeric perimeter identifier
- `PerimeterName`: Display name for the perimeter
- `BU_Id`: Department ID from departments.csv
- `BU_Name`: Department display name

### 3. `acl.csv`
Defines user access control - grants users access to one or more perimeters or departments.

**Format:**
```csv
User,AccessLevel,Id
User 1,Perimeter,1
User 2,Perimeter,2
User 3,Business Unit,54000211461
```

- `User`: Username identifier
- `AccessLevel`: Either "Perimeter" (access to all departments in a perimeter) or "Business Unit" (access to specific department)
- `Id`: Perimeter ID (if AccessLevel=Perimeter) or Department ID (if AccessLevel=Business Unit)

## Scripts

### 1. `freshdesk_api.py`
Retrieves the most recent open ticket with enriched display names for various ID fields.

**Usage:**
```bash
python freshdesk_api.py
```

### 2. `get_incident.py`
Retrieves the most recent open incident (filters by type='Incident').

**Usage:**
```bash
python get_incident.py
```

### 3. `get_service_request.py`
Retrieves the most recent open service request (filters by type='Service Request').

**Usage:**
```bash
python get_service_request.py
```

### 4. `get_incident_counts.py` (Main Script)
Generates a comprehensive incident count report with optional ACL-based filtering.

**Features:**
- Counts incidents raised in the last N days (default: 30)
- Filters by status: Open, Pending, Resolved, Closed
- Applies organizational access control based on user permissions
- Provides resolution rate statistics
- Optional JSON export

**Usage:**
```bash
python get_incident_counts.py
```

**Interactive prompts:**
1. Enter username for ACL filtering (or leave blank for all data)
2. Enter number of days to analyze (default: 30)
3. Optionally save results to JSON

**Example Output:**
```
User has access to 4 department(s):
  - [54000211461] DESKTOP 2026 AXIANS BASINGSTOKE
  - [54000211462] DESKTOP 2026 AXIANS PERIMETER SUPPORT
  - [54000211463] DESKTOP 2026 AXIANS COVENTRY
  - [54000211465] DESKTOP 2026 AXIANS WOKINGHAM

╔════════════════════════════════════════════════════════════════════════
║ FRESHSERVICE INCIDENT COUNT REPORT
╠════════════════════════════════════════════════════════════════════════
║ User: User 1
║ ACL Filter: Applied
║ Date Range: Last 30 days
╠════════════════════════════════════════════════════════════════════════
║ Total Incidents Raised:          45
║ Total Incidents Resolved:         32
║ Total Incidents Open:              8
╠════════════════════════════════════════════════════════════════════════
║ Resolution Rate:                71.1%
╚════════════════════════════════════════════════════════════════════════
```

### 5. `incident_dashboard.py`
Interactive dashboard showing incident metrics based on user role (department manager vs individual employee).

**Usage:**
```bash
python incident_dashboard.py
```

### 6. `match_departments.py`
Utility script to match business unit names from perimeters.csv with department IDs from departments.csv.

**Usage:**
```bash
python match_departments.py
```

## Access Control Examples

### Example 1: Perimeter Access
User gets access to all departments under a perimeter:
```csv
User 1,Perimeter,1
```
→ User 1 can see all incidents from Axians departments (4 departments)

### Example 2: Multiple Perimeter Access
User gets access to multiple perimeters:
```csv
User 2,Perimeter,1
User 2,Perimeter,2
```
→ User 2 can see incidents from both Axians and Actemium Automation

### Example 3: Specific Department Access
User gets access to individual departments:
```csv
User 3,Business Unit,54000211461
User 3,Business Unit,54000211463
```
→ User 3 can only see incidents from these two specific departments

### Example 4: Mixed Access
User can have both perimeter and department level access:
```csv
User 4,Perimeter,1
User 4,Business Unit,54000227469
```
→ User 4 sees all Axians departments plus Actemium Design

## File Structure

```
fresh-desk-api/
├── data/
│   ├── departments.csv      # Department IDs and names
│   ├── perimeters.csv        # Perimeter to department mappings
│   └── acl.csv               # User access control list
├── archive/                  # Backup files
├── freshdesk_api.py          # General ticket retrieval
├── get_incident.py           # Incident retrieval
├── get_service_request.py    # Service request retrieval
├── get_incident_counts.py    # Main counting script with ACL
├── incident_dashboard.py     # Interactive dashboard
├── match_departments.py      # Department matching utility
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## API Reference

### FreshService API v2 Endpoints Used:
- `GET /api/v2/tickets` - Retrieve tickets with pagination
- `GET /api/v2/departments` - Retrieve departments (if needed)
- `GET /api/v2/requesters` - Retrieve requester information
- `GET /api/v2/agents` - Retrieve agent information
- `GET /api/v2/groups` - Retrieve groups

### Status Codes:
- `2` - Open
- `3` - Pending
- `4` - Resolved
- `5` - Closed

### Priority Codes:
- `1` - Low
- `2` - Medium
- `3` - High
- `4` - Urgent

## Notes

- All CSV files use UTF-8 encoding with BOM support
- The scripts handle both list and dict responses from the API
- Pagination is implemented with a safety limit of 50 pages
- Date filtering uses timezone-aware datetime comparisons
- Department filtering is performed by numeric ID matching for accuracy

## Troubleshooting

**Issue**: "No ACL found for user"
- Verify the username exists in `data/acl.csv`
- Check for UTF-8 BOM issues in CSV files

**Issue**: "No department restrictions apply" despite having ACL
- Verify the perimeter/department IDs in acl.csv match those in perimeters.csv and departments.csv
- Check for numeric ID type mismatches

**Issue**: Zero incidents returned
- Verify the date range includes relevant data
- Check if the user's departments have any incidents in the time period
- Ensure department IDs in tickets match those in your CSV files

## Contributing

When adding new users or departments:
1. Update `data/departments.csv` with new department IDs from FreshService
2. Add departments to appropriate perimeters in `data/perimeters.csv`
3. Grant user access in `data/acl.csv`

## License

Internal use only.