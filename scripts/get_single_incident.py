#!/usr/bin/env python3
"""
FreshDesk API Script - Incidents
Retrieves the most recent open incident from FreshDesk
"""

import requests
from datetime import datetime


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


def get_display_name(item_id, endpoint, name_field='name'):
    """
    Fetches display name for a given ID from an API endpoint
    
    Args:
        item_id: The ID to look up
        endpoint (str): API endpoint to query
        name_field (str): Field name containing the display name
        
    Returns:
        str: Display name or original ID if not found
    """
    if not item_id:
        return 'N/A'
    
    data = fetch_api_data(f"{endpoint}/{item_id}")
    
    if data:
        # Handle wrapped responses
        if isinstance(data, dict):
            if endpoint.rstrip('s') in data:
                data = data[endpoint.rstrip('s')]
            return data.get(name_field, str(item_id))
    
    return str(item_id)


def enrich_ticket_data(ticket):
    """
    Enriches ticket data with display names for IDs
    
    Args:
        ticket (dict): Ticket data from API
        
    Returns:
        dict: Enriched ticket data with display names
    """
    if not ticket:
        return ticket
    
    enriched = ticket.copy()
    
    # Map of field to (endpoint, name_field)
    lookups = {
        'group_id': ('groups', 'name'),
        'department_id': ('departments', 'name'),
        'requester_id': ('requesters', 'primary_email'),
        'requested_for_id': ('requesters', 'primary_email'),
        'workspace_id': ('workspaces', 'name'),
    }
    
    # Priority mapping (FreshService standard values)
    priority_map = {1: 'Low', 2: 'Medium', 3: 'High', 4: 'Urgent'}
    
    # Status mapping (FreshService standard values)
    status_map = {
        2: 'Open',
        3: 'Pending',
        4: 'Resolved',
        5: 'Closed',
        6: 'Waiting on Customer',
        7: 'Waiting on Third Party'
    }
    
    # Source mapping (FreshService standard values)
    source_map = {
        1: 'Email',
        2: 'Portal',
        3: 'Phone',
        4: 'Chat',
        5: 'Feedback widget',
        6: 'Yammer',
        7: 'AWS Cloudwatch',
        8: 'Pagerduty',
        9: 'Walkup',
        10: 'Slack'
    }
    
    # Enrich with display names from API
    for field, (endpoint, name_field) in lookups.items():
        if field in ticket and ticket[field]:
            display_name = get_display_name(ticket[field], endpoint, name_field)
            enriched[f'{field}_name'] = display_name
    
    # Enrich with mapped values
    if 'priority' in ticket:
        enriched['priority_name'] = priority_map.get(ticket['priority'], f"Priority {ticket['priority']}")
    
    if 'status' in ticket:
        enriched['status_name'] = status_map.get(ticket['status'], f"Status {ticket['status']}")
    
    if 'source' in ticket:
        enriched['source_name'] = source_map.get(ticket['source'], f"Source {ticket['source']}")
    
    return enriched


def get_recent_open_incident():
    """
    Fetches the most recent open incident from FreshService API
    
    Returns:
        dict: The most recent open incident data (enriched with display names), or None if no incidents found
    """
    params = {
        'filter': 'new_and_my_open',
        'order_by': 'created_at',
        'order_type': 'desc',
        'per_page': 100  # Get more to filter by type
    }
    
    # Use the tickets endpoint
    data = fetch_api_data('tickets', params)
    
    if not data:
        return None
    
    try:
        # Handle different response formats
        tickets = []
        if isinstance(data, list):
            tickets = data
        elif isinstance(data, dict):
            if 'tickets' in data:
                tickets = data['tickets']
            else:
                tickets = [data]
        
        # Filter for Incidents only (exclude Service Requests)
        incidents = []
        for ticket in tickets:
            ticket_type = ticket.get('type', '')
            
            # Filter for incidents only
            if ticket_type and 'incident' in ticket_type.lower():
                incidents.append(ticket)
        
        # If we found incidents, return the first (most recent)
        if incidents:
            return enrich_ticket_data(incidents[0])
        
        # If no specific incidents found
        print(f"Note: Found {len(tickets)} ticket(s), but no incidents.")
        if tickets:
            print(f"First ticket type: {tickets[0].get('type', 'Unknown')}")
        
        return None
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(f"Response type: {type(data)}")
        print(f"Response data: {data}")
        return None


def format_incident_info(incident):
    """
    Formats incident information for display
    
    Args:
        incident (dict): Incident data from API
        
    Returns:
        str: Formatted incident information
    """
    if not incident:
        return "No open incidents found."
    
    incident_info = f"""
╔══════════════════════════════════════════════════════════════
║ MOST RECENT OPEN INCIDENT
╠══════════════════════════════════════════════════════════════
║ Incident ID:      {incident.get('id', 'N/A')}
║ Subject:          {incident.get('subject', 'N/A')}
║ 
║ Status:           {incident.get('status_name', incident.get('status', 'N/A'))}
║ Priority:         {incident.get('priority_name', incident.get('priority', 'N/A'))}
║ Source:           {incident.get('source_name', incident.get('source', 'N/A'))}
║ 
║ Requester:        {incident.get('requester_id_name', incident.get('requester_id', 'N/A'))}
║ Requested For:    {incident.get('requested_for_id_name', incident.get('requested_for_id', 'N/A'))}
║ Group:            {incident.get('group_id_name', incident.get('group_id', 'N/A'))}
║ Department:       {incident.get('department_id_name', incident.get('department_id', 'N/A'))}
║ Workspace:        {incident.get('workspace_id_name', incident.get('workspace_id', 'N/A'))}
║ 
║ Created At:       {incident.get('created_at', 'N/A')}
║ Updated At:       {incident.get('updated_at', 'N/A')}
║ 
║ Description:      {incident.get('description_text', incident.get('description', 'N/A'))[:80]}...
╚══════════════════════════════════════════════════════════════
"""
    return incident_info


def main():
    """Main execution function"""
    print("Fetching most recent open incident from FreshService...")
    print(f"Instance: {INSTANCE_URL}\n")
    
    incident = get_recent_open_incident()
    
    if incident:
        print(format_incident_info(incident))
        print("\nFull incident data:")
        import json
        print(json.dumps(incident, indent=2))
    else:
        print("No open incidents found or error occurred.")


if __name__ == "__main__":
    main()
