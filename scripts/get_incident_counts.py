#!/usr/bin/env python3
"""
FreshService Incident Count Script
Gets counts of incidents raised in the last 30 days with efficient API usage
Includes CSV-based access control for organizational hierarchy
"""

import requests
from datetime import datetime, timedelta
import csv
import os


# Configuration
INSTANCE_URL = "axiansnetworkltd.freshservice.com"
API_KEY = "kGALZPRyHlTmnvDEmnuh"
API_BASE_URL = f"https://{INSTANCE_URL}/api/v2"
PERIMETERS_FILE = "data/perimeters.csv"
DEPARTMENTS_FILE = "data/departments.csv"
ACL_FILE = "data/acl.csv"


def fetch_api_data(endpoint, params=None):
    """
    Generic function to fetch data from FreshService API
    
    Args:
        endpoint (str): API endpoint path
        params (dict): Query parameters
        
    Returns:
        dict or list: API response data, or None if error
    """
    auth = (API_KEY, 'X')
    url = f"{API_BASE_URL}/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.get(url, auth=auth, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {endpoint}: {e}")
        return None


def load_departments(filename=DEPARTMENTS_FILE):
    """
    Load department IDs and names from CSV file
    
    Args:
        filename (str): Path to departments CSV file
        
    Returns:
        dict: Mapping of department_id to department_name
    """
    dept_map = {}
    
    if not os.path.exists(filename):
        print(f"Warning: {filename} not found. Cannot load departments.")
        return dept_map
    
    with open(filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dept_id = row.get('ID', '').strip()
            dept_name = row.get('Name', '').strip()
            if dept_id and dept_name:
                try:
                    dept_map[int(dept_id)] = dept_name
                except ValueError:
                    pass  # Skip invalid IDs
    
    return dept_map


def load_perimeters(filename=PERIMETERS_FILE):
    """
    Load perimeter structure from CSV file
    
    Args:
        filename (str): Path to perimeters CSV file
        
    Returns:
        dict: Dictionary mapping perimeter IDs to list of department IDs
    """
    perimeter_map = {}
    
    if not os.path.exists(filename):
        print(f"Warning: {filename} not found. Proceeding without perimeter filtering.")
        return perimeter_map
    
    with open(filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            perimeter_id = row.get('Id', '').strip()
            bu_id = row.get('BU_Id', '').strip()
            
            if perimeter_id and bu_id:
                try:
                    peri_id = int(perimeter_id)
                    dept_id = int(bu_id)
                    if peri_id not in perimeter_map:
                        perimeter_map[peri_id] = []
                    perimeter_map[peri_id].append(dept_id)
                except ValueError:
                    pass  # Skip invalid IDs
    
    return perimeter_map


def load_user_acl(username, filename=ACL_FILE):
    """
    Load user's access control list from CSV
    
    Args:
        username (str): Username to look up
        filename (str): Path to ACL CSV file
        
    Returns:
        list: List of tuples (access_level, id) where id is perimeter_id or department_id
    """
    user_acl = []
    
    if not os.path.exists(filename):
        print(f"Warning: {filename} not found. Proceeding without ACL filtering.")
        return user_acl
    
    with open(filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user = row.get('User', '').strip()
            access_level = row.get('AccessLevel', '').strip()
            id_value = row.get('Id', '').strip()
            
            if user == username and access_level and id_value:
                try:
                    user_acl.append((access_level, int(id_value)))
                except ValueError:
                    pass  # Skip invalid IDs
    
    return user_acl


def get_allowed_department_ids(username, perimeter_map, dept_map):
    """
    Get list of department IDs user has access to based on ACL
    
    Args:
        username (str): Username to check
        perimeter_map (dict): Perimeter ID to department IDs mapping
        dept_map (dict): Department ID to name mapping
        
    Returns:
        set: Set of department IDs user can access (None for all)
    """
    user_acl = load_user_acl(username)
    
    if not user_acl:
        print(f"Warning: No ACL found for user '{username}'. No department filtering applied.")
        return None  # None means no filtering
    
    allowed_dept_ids = set()
    
    for access_level, id_value in user_acl:
        if access_level == "Perimeter":
            # id_value is a perimeter ID - get all departments under this perimeter
            if id_value in perimeter_map:
                allowed_dept_ids.update(perimeter_map[id_value])
        elif access_level == "Business Unit":
            # id_value is a department ID directly
            allowed_dept_ids.add(id_value)
    
    return allowed_dept_ids if allowed_dept_ids else None


def get_incident_count(status_filter=None, days=30, allowed_dept_ids=None):
    """
    Get count of incidents using efficient API pagination
    
    Args:
        status_filter (list): List of status codes to filter (None for all)
        days (int): Number of days to look back
        allowed_dept_ids (set): Set of department IDs user can access (None for all)
        
    Returns:
        int: Count of incidents
    """
    from datetime import timezone
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    updated_since = cutoff_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    count = 0
    page = 1
    per_page = 100
    max_pages = 50
    
    params = {
        'per_page': per_page,
        'updated_since': updated_since
    }
    
    auth = (API_KEY, 'X')
    url = f"{API_BASE_URL}/tickets"
    headers = {'Content-Type': 'application/json'}
    
    while page <= max_pages:
        params['page'] = page
        
        try:
            response = requests.get(url, auth=auth, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Handle both list and dict responses
            tickets = data if isinstance(data, list) else data.get('tickets', [])
            
            if not tickets:
                break
            
            for ticket in tickets:
                # Check if it's an incident
                ticket_type = ticket.get('type', '')
                if ticket_type != 'Incident':
                    continue
                
                # Verify date is within range
                updated_at = ticket.get('updated_at', '')
                if updated_at:
                    ticket_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    if ticket_date < cutoff_date:
                        continue
                
                # Apply status filter if provided
                if status_filter and ticket.get('status') not in status_filter:
                    continue
                
                # Apply department filter if provided
                if allowed_dept_ids is not None:
                    dept_id = ticket.get('department_id')
                    if dept_id not in allowed_dept_ids:
                        continue
                
                count += 1
            
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching tickets: {e}")
            break
    
    return count


def get_incident_counts_summary(days=30, username=None):
    """
    Get summary of incident counts with optional ACL filtering
    
    Args:
        days (int): Number of days to look back
        username (str): Username for ACL filtering (None for no filtering)
        
    Returns:
        dict: Dictionary with incident counts
    """
    print(f"Fetching incident counts for the last {days} days...")
    
    # Load department and perimeter data
    dept_map = load_departments()
    print(f"Loaded {len(dept_map)} departments from CSV")
    
    # Determine allowed departments
    allowed_dept_ids = None
    
    if username:
        print(f"\nApplying ACL for user: {username}")
        perimeter_map = load_perimeters()
        allowed_dept_ids = get_allowed_department_ids(username, perimeter_map, dept_map)
        
        if allowed_dept_ids:
            print(f"\nUser has access to {len(allowed_dept_ids)} department(s):")
            for dept_id in sorted(allowed_dept_ids):
                dept_name = dept_map.get(dept_id, f"Unknown (ID: {dept_id})")
                print(f"  - [{dept_id}] {dept_name}")
        else:
            print("\nNo department restrictions apply")
    else:
        print("\nNo ACL filtering (counting all incidents)")
    
    print("\nThis may take a moment...\n")
    
    # Status codes in FreshService:
    # 2 = Open
    # 3 = Pending
    # 4 = Resolved
    # 5 = Closed
    
    # Get total incidents raised (all statuses)
    print("Counting total incidents raised...")
    total_raised = get_incident_count(
        status_filter=None, 
        days=days, 
        allowed_dept_ids=allowed_dept_ids
    )
    
    # Get resolved/closed incidents (status 4 or 5)
    print("Counting resolved incidents...")
    total_resolved = get_incident_count(
        status_filter=[4, 5], 
        days=days,
        allowed_dept_ids=allowed_dept_ids
    )
    
    # Get open/pending incidents (status 2 or 3)
    print("Counting open incidents...")
    total_open = get_incident_count(
        status_filter=[2, 3], 
        days=days,
        allowed_dept_ids=allowed_dept_ids
    )
    
    return {
        'total_raised': total_raised,
        'total_resolved': total_resolved,
        'total_open': total_open,
        'days': days,
        'username': username,
        'department_filter_applied': allowed_dept_ids is not None,
        'generated_at': datetime.now().isoformat()
    }


def display_counts(counts):
    """
    Display incident counts in a formatted manner
    
    Args:
        counts (dict): Dictionary with incident counts
    """
    user_info = f"║ User: {counts.get('username', 'N/A')}\n" if counts.get('username') else ""
    acl_info = f"║ ACL Filter: {'Applied' if counts.get('department_filter_applied') else 'Not Applied'}\n" if counts.get('username') else ""
    
    report = f"""
╔════════════════════════════════════════════════════════════════════════
║ FRESHSERVICE INCIDENT COUNT REPORT
╠════════════════════════════════════════════════════════════════════════
{user_info}{acl_info}║ Date Range: Last {counts['days']} days
║ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
╠════════════════════════════════════════════════════════════════════════
║ INCIDENT COUNTS
╠════════════════════════════════════════════════════════════════════════
║ Total Incidents Raised:       {counts['total_raised']:>6}
║ Total Incidents Resolved:     {counts['total_resolved']:>6}
║ Total Incidents Open:         {counts['total_open']:>6}
╠════════════════════════════════════════════════════════════════════════
║ STATISTICS
╠════════════════════════════════════════════════════════════════════════
║ Resolution Rate:               {(counts['total_resolved'] / counts['total_raised'] * 100) if counts['total_raised'] > 0 else 0:>5.1f}%
║ Open Rate:                     {(counts['total_open'] / counts['total_raised'] * 100) if counts['total_raised'] > 0 else 0:>5.1f}%
╚════════════════════════════════════════════════════════════════════════
"""
    print(report)


def main():
    """Main execution function"""
    print("FreshService Incident Count Script with ACL")
    print("=" * 70)
    
    # Get username for ACL
    username_input = input("\nEnter username for ACL filtering (leave blank for no filtering): ").strip()
    username = username_input if username_input else None
    
    # Get date range
    days_input = input("Number of days to analyze (default 30): ").strip()
    days = int(days_input) if days_input.isdigit() else 30
    
    # Get counts
    counts = get_incident_counts_summary(days, username)
    
    # Display results
    display_counts(counts)
    
    # Optional: Save to JSON
    save_report = input("\nSave report to JSON? (yes/no): ").strip().lower()
    if save_report == 'yes':
        import json
        filename = f"incident_counts_{username or 'all'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(counts, f, indent=2)
        print(f"\nReport saved to: {filename}")


if __name__ == "__main__":
    main()
