#!/usr/bin/env python3
"""
FreshService Incident Dashboard
Provides metrics for incidents based on user context (department manager or individual employee)
"""

import requests
from datetime import datetime, timedelta
from collections import defaultdict
import json


# Configuration
INSTANCE_URL = "axiansnetworkltd.freshservice.com"
API_KEY = "kGALZPRyHlTmnvDEmnuh"
API_BASE_URL = f"https://{INSTANCE_URL}/api/v2"


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


def get_user_info(user_email):
    """
    Get user information including department
    
    Args:
        user_email (str): User's email address
        
    Returns:
        dict: User information or None
    """
    # Get all requesters and search for the email
    # FreshService doesn't support email search in query, so we fetch and filter
    page = 1
    per_page = 100
    
    while True:
        params = {'per_page': per_page, 'page': page}
        data = fetch_api_data('requesters', params)
        
        if not data:
            break
        
        requesters = []
        if isinstance(data, list):
            requesters = data
        elif isinstance(data, dict) and 'requesters' in data:
            requesters = data['requesters']
        
        if not requesters:
            break
        
        # Search for matching email
        for requester in requesters:
            email = requester.get('primary_email', '') or ''
            if email.lower() == user_email.lower():
                return requester
        
        # Check if there are more pages
        if len(requesters) < per_page:
            break
        
        page += 1
    
    return None


def get_department_users(department_id):
    """
    Get all users in a department
    
    Args:
        department_id: Department ID
        
    Returns:
        list: List of user IDs in the department
    """
    user_ids = []
    page = 1
    per_page = 100
    
    while True:
        params = {'per_page': per_page, 'page': page}
        data = fetch_api_data('requesters', params)
        
        if not data:
            break
        
        requesters = []
        if isinstance(data, list):
            requesters = data
        elif isinstance(data, dict) and 'requesters' in data:
            requesters = data['requesters']
        
        if not requesters:
            break
        
        # Filter users by department
        for requester in requesters:
            if requester.get('department_id') == department_id:
                user_ids.append(requester['id'])
        
        # Check if there are more pages
        if len(requesters) < per_page:
            break
        
        page += 1
    
    return user_ids


def get_all_incidents(user_context, is_department_head=False, days=30):
    """
    Fetch all incidents based on user context from the last N days
    
    Args:
        user_context (dict): User information including department_id
        is_department_head (bool): Whether user is a department head
        days (int): Number of days to look back (default: 30)
        
    Returns:
        list: List of incidents
    """
    all_incidents = []
    page = 1
    per_page = 100
    
    # Calculate date filter (last N days)
    cutoff_date = datetime.now() - timedelta(days=days)
    cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
    
    print(f"Fetching incidents from the last {days} days (since {cutoff_date_str})...")
    
    while True:
        params = {
            'per_page': per_page,
            'page': page,
            'updated_since': cutoff_date_str  # Filter by updated date
        }
        
        data = fetch_api_data('tickets', params)
        
        if not data:
            break
            
        incidents = []
        if isinstance(data, list):
            incidents = data
        elif isinstance(data, dict) and 'tickets' in data:
            incidents = data['tickets']
        
        if not incidents:
            break
        
        # Filter for incidents only (not service requests)
        for ticket in incidents:
            ticket_type = ticket.get('type', '')
            if ticket_type and 'incident' in ticket_type.lower():
                # Double-check date filter (API filter may not be exact)
                created_at = ticket.get('created_at')
                if created_at:
                    try:
                        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if created >= cutoff_date:
                            all_incidents.append(ticket)
                    except:
                        # If date parsing fails, include the ticket anyway
                        all_incidents.append(ticket)
                else:
                    all_incidents.append(ticket)
        
        # Check if there are more pages
        if len(incidents) < per_page:
            break
            
        page += 1
        
        # Safety limit to prevent infinite loops
        if page > 50:  # Max 5000 tickets
            print(f"Warning: Reached maximum page limit (50 pages)")
            break
    
    # Filter based on user context
    if is_department_head and user_context.get('department_id'):
        # Get all users in the department
        dept_user_ids = get_department_users(user_context['department_id'])
        
        # Filter incidents for department users
        filtered_incidents = [
            inc for inc in all_incidents 
            if inc.get('requester_id') in dept_user_ids or 
               inc.get('requested_for_id') in dept_user_ids
        ]
        return filtered_incidents
    else:
        # Individual employee - only their tickets
        user_id = user_context.get('id')
        filtered_incidents = [
            inc for inc in all_incidents 
            if inc.get('requester_id') == user_id or 
               inc.get('requested_for_id') == user_id
        ]
        return filtered_incidents


def calculate_resolution_time(incident):
    """
    Calculate resolution time for an incident in hours
    
    Args:
        incident (dict): Incident data
        
    Returns:
        float: Resolution time in hours, or None if not resolved
    """
    # Status 4 = Resolved, Status 5 = Closed
    if incident.get('status') not in [4, 5]:
        return None
    
    created_at = incident.get('created_at')
    updated_at = incident.get('updated_at')
    
    if not created_at or not updated_at:
        return None
    
    try:
        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        resolved = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        
        resolution_time = (resolved - created).total_seconds() / 3600  # Convert to hours
        return resolution_time
    except:
        return None


def calculate_metrics(incidents):
    """
    Calculate all metrics for incidents
    
    Args:
        incidents (list): List of incidents
        
    Returns:
        dict: Dictionary containing all metrics
    """
    metrics = {
        'total_incidents': len(incidents),
        'tickets_raised': 0,
        'completed_tickets': 0,
        'in_progress': 0,
        'high_priority': 0,
        'medium_priority': 0,
        'low_priority': 0,
        'urgent_priority': 0,
        'avg_resolution_time': None,
        'longest_resolution_time': None,
        'shortest_resolution_time': None,
        'resolution_times': []
    }
    
    resolution_times = []
    
    # Status mapping
    # 2 = Open, 3 = Pending, 4 = Resolved, 5 = Closed
    for incident in incidents:
        status = incident.get('status')
        priority = incident.get('priority')
        
        # Count tickets raised (all statuses)
        metrics['tickets_raised'] += 1
        
        # Count completed tickets (Resolved or Closed)
        if status in [4, 5]:
            metrics['completed_tickets'] += 1
        
        # Count in progress (Open or Pending)
        if status in [2, 3]:
            metrics['in_progress'] += 1
        
        # Priority breakdown (1=Low, 2=Medium, 3=High, 4=Urgent)
        if priority == 1:
            metrics['low_priority'] += 1
        elif priority == 2:
            metrics['medium_priority'] += 1
        elif priority == 3:
            metrics['high_priority'] += 1
        elif priority == 4:
            metrics['urgent_priority'] += 1
        
        # Calculate resolution times
        resolution_time = calculate_resolution_time(incident)
        if resolution_time is not None:
            resolution_times.append(resolution_time)
    
    # Calculate resolution time metrics
    if resolution_times:
        metrics['avg_resolution_time'] = sum(resolution_times) / len(resolution_times)
        metrics['longest_resolution_time'] = max(resolution_times)
        metrics['shortest_resolution_time'] = min(resolution_times)
        metrics['resolution_times'] = resolution_times
    
    return metrics


def format_time(hours):
    """
    Format time in hours to a human-readable format
    
    Args:
        hours (float): Time in hours
        
    Returns:
        str: Formatted time string
    """
    if hours is None:
        return 'N/A'
    
    days = int(hours // 24)
    remaining_hours = int(hours % 24)
    minutes = int((hours * 60) % 60)
    
    if days > 0:
        return f"{days}d {remaining_hours}h {minutes}m"
    elif remaining_hours > 0:
        return f"{remaining_hours}h {minutes}m"
    else:
        return f"{minutes}m"


def display_dashboard(metrics, user_name, context_type, days=30):
    """
    Display the dashboard metrics
    
    Args:
        metrics (dict): Calculated metrics
        user_name (str): User's name
        context_type (str): 'Department Manager' or 'Individual Employee'
        days (int): Number of days the report covers
    """
    dashboard = f"""
╔════════════════════════════════════════════════════════════════════════
║ FRESHSERVICE INCIDENT DASHBOARD
╠════════════════════════════════════════════════════════════════════════
║ User: {user_name}
║ Context: {context_type}
║ Date Range: Last {days} days
║ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
╠════════════════════════════════════════════════════════════════════════
║ INCIDENT BREAKDOWN
╠════════════════════════════════════════════════════════════════════════
║ Total Incidents Reported:     {metrics['total_incidents']:>6}
║ Tickets Raised:                {metrics['tickets_raised']:>6}
║ Completed Tickets:             {metrics['completed_tickets']:>6}
║ In Progress:                   {metrics['in_progress']:>6}
╠════════════════════════════════════════════════════════════════════════
║ PRIORITY BREAKDOWN
╠════════════════════════════════════════════════════════════════════════
║ Urgent Priority:               {metrics['urgent_priority']:>6}
║ High Priority:                 {metrics['high_priority']:>6}
║ Medium Priority:               {metrics['medium_priority']:>6}
║ Low Priority:                  {metrics['low_priority']:>6}
╠════════════════════════════════════════════════════════════════════════
║ RESOLUTION TIME METRICS
╠════════════════════════════════════════════════════════════════════════
║ Average Resolution Time:       {format_time(metrics['avg_resolution_time']):>15}
║ Longest Resolution Time:       {format_time(metrics['longest_resolution_time']):>15}
║ Shortest Resolution Time:      {format_time(metrics['shortest_resolution_time']):>15}
╚════════════════════════════════════════════════════════════════════════
"""
    print(dashboard)


def main():
    """Main execution function"""
    print("FreshService Incident Dashboard")
    print("=" * 70)
    
    # Get user context
    user_email = input("\nEnter your email address: ").strip()
    is_dept_head = input("Are you a department head? (yes/no): ").strip().lower() == 'yes'
    
    # Get date range (default 30 days)
    days_input = input("Number of days to analyze (default 30): ").strip()
    days = int(days_input) if days_input.isdigit() else 30
    
    print("\nFetching user information...")
    user_info = get_user_info(user_email)
    
    if not user_info:
        print(f"Error: Could not find user with email {user_email}")
        return
    
    user_name = user_info.get('first_name', '') + ' ' + user_info.get('last_name', '')
    user_name = user_name.strip() or user_email
    
    context_type = "Department Manager" if is_dept_head else "Individual Employee"
    
    print(f"User: {user_name}")
    print(f"Department ID: {user_info.get('department_id', 'N/A')}")
    print(f"Context: {context_type}")
    
    print(f"\nFetching incidents from the last {days} days...")
    incidents = get_all_incidents(user_info, is_dept_head, days)
    
    print(f"Found {len(incidents)} incident(s)")
    
    print("\nCalculating metrics...")
    metrics = calculate_metrics(incidents)
    
    # Display dashboard
    display_dashboard(metrics, user_name, context_type, days)
    
    # Optional: Save detailed report to JSON
    save_report = input("\nSave detailed report to JSON? (yes/no): ").strip().lower()
    if save_report == 'yes':
        report = {
            'user': user_name,
            'email': user_email,
            'context': context_type,
            'date_range_days': days,
            'generated_at': datetime.now().isoformat(),
            'metrics': {
                'total_incidents': metrics['total_incidents'],
                'tickets_raised': metrics['tickets_raised'],
                'completed_tickets': metrics['completed_tickets'],
                'in_progress': metrics['in_progress'],
                'high_priority': metrics['high_priority'],
                'medium_priority': metrics['medium_priority'],
                'low_priority': metrics['low_priority'],
                'urgent_priority': metrics['urgent_priority'],
                'avg_resolution_time_hours': metrics['avg_resolution_time'],
                'longest_resolution_time_hours': metrics['longest_resolution_time'],
                'shortest_resolution_time_hours': metrics['shortest_resolution_time']
            },
            'incident_count': len(incidents)
        }
        
        filename = f"incident_report_{user_email.split('@')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to: {filename}")


if __name__ == "__main__":
    main()
