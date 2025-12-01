#!/usr/bin/env python3
"""
FreshDesk API Script - Service Requests
Retrieves the most recent open service request from FreshDesk
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


def enrich_service_request_data(sr):
    """
    Enriches service request data with display names for IDs
    
    Args:
        sr (dict): Service request data from API
        
    Returns:
        dict: Enriched service request data with display names
    """
    if not sr:
        return sr
    
    enriched = sr.copy()
    
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
    
    # Status mapping (FreshService standard values for Service Requests)
    status_map = {
        1: 'Open',
        2: 'In Progress',
        3: 'Waiting on Customer',
        4: 'Waiting on Third Party',
        5: 'Pending Approval',
        6: 'Approved',
        7: 'Rejected',
        8: 'Closed',
        9: 'Cancelled'
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
        if field in sr and sr[field]:
            display_name = get_display_name(sr[field], endpoint, name_field)
            enriched[f'{field}_name'] = display_name
    
    # Enrich with mapped values
    if 'priority' in sr:
        enriched['priority_name'] = priority_map.get(sr['priority'], f"Priority {sr['priority']}")
    
    if 'status' in sr:
        enriched['status_name'] = status_map.get(sr['status'], f"Status {sr['status']}")
    
    if 'source' in sr:
        enriched['source_name'] = source_map.get(sr['source'], f"Source {sr['source']}")
    
    return enriched


def get_recent_open_service_request():
    """
    Fetches the most recent open service request from FreshService API
    
    Returns:
        dict: The most recent open service request data (enriched with display names), or None if no service requests found
    """
    params = {
        'filter': 'new_and_my_open',
        'order_by': 'created_at',
        'order_type': 'desc',
        'per_page': 100  # Get more to filter by type
    }
    
    # Service requests are accessed via tickets endpoint in FreshService
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
            elif 'service_requests' in data:
                tickets = data['service_requests']
            else:
                tickets = [data]
        
        # Filter for Service Request type
        # In FreshService, the 'type' field contains either 'Service Request' or 'Incident'
        service_requests = []
        for ticket in tickets:
            ticket_type = ticket.get('type', '')
            
            # Filter for service requests (case-insensitive check)
            if ticket_type and 'service request' in ticket_type.lower():
                service_requests.append(ticket)
        
        # If we found service requests, return the first (most recent)
        if service_requests:
            return enrich_service_request_data(service_requests[0])
        
        # If no specific service requests found
        print(f"Note: Found {len(tickets)} ticket(s), but no service requests.")
        if tickets:
            print(f"First ticket type: {tickets[0].get('type', 'Unknown')}")
        
        return None
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(f"Response type: {type(data)}")
        print(f"Response data: {data}")
        return None


def format_service_request_info(sr):
    """
    Formats service request information for display
    
    Args:
        sr (dict): Service request data from API
        
    Returns:
        str: Formatted service request information
    """
    if not sr:
        return "No open service requests found."
    
    sr_info = f"""
╔══════════════════════════════════════════════════════════════
║ MOST RECENT OPEN SERVICE REQUEST
╠══════════════════════════════════════════════════════════════
║ Request ID:       {sr.get('id', 'N/A')}
║ Subject:          {sr.get('subject', 'N/A')}
║ 
║ Status:           {sr.get('status_name', sr.get('status', 'N/A'))}
║ Priority:         {sr.get('priority_name', sr.get('priority', 'N/A'))}
║ Source:           {sr.get('source_name', sr.get('source', 'N/A'))}
║ 
║ Requester:        {sr.get('requester_id_name', sr.get('requester_id', 'N/A'))}
║ Requested For:    {sr.get('requested_for_id_name', sr.get('requested_for_id', 'N/A'))}
║ Group:            {sr.get('group_id_name', sr.get('group_id', 'N/A'))}
║ Department:       {sr.get('department_id_name', sr.get('department_id', 'N/A'))}
║ Workspace:        {sr.get('workspace_id_name', sr.get('workspace_id', 'N/A'))}
║ 
║ Created At:       {sr.get('created_at', 'N/A')}
║ Updated At:       {sr.get('updated_at', 'N/A')}
║ 
║ Description:      {sr.get('description_text', sr.get('description', 'N/A'))[:80]}...
╚══════════════════════════════════════════════════════════════
"""
    return sr_info


def main():
    """Main execution function"""
    print("Fetching most recent open service request from FreshService...")
    print(f"Instance: {INSTANCE_URL}\n")
    
    sr = get_recent_open_service_request()
    
    if sr:
        print(format_service_request_info(sr))
        print("\nFull service request data:")
        import json
        print(json.dumps(sr, indent=2))
    else:
        print("No open service requests found or error occurred.")


if __name__ == "__main__":
    main()
