#!/usr/bin/env python3
"""
FreshDesk API Script
Retrieves the most recent open ticket from FreshDesk
"""

import requests
import base64
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
        'requester_id': ('requesters', 'primary_email'),  # or 'name'
        'requested_for_id': ('requesters', 'primary_email'),  # or 'name'
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


def get_recent_open_ticket():
    """
    Fetches the most recent open ticket from FreshDesk API
    
    Returns:
        dict: The most recent open ticket data (enriched with display names), or None if no tickets found
    """
    params = {
        'filter': 'new_and_my_open',  # Filter for open tickets
        'order_by': 'created_at',
        'order_type': 'desc',
        'per_page': 1  # Only get the most recent one
    }
    
    url = f"{API_BASE_URL}/tickets"
    auth = (API_KEY, 'X')
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, auth=auth, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different response formats
        ticket = None
        if isinstance(data, list):
            # Response is a list of tickets
            if len(data) > 0:
                ticket = data[0]
        elif isinstance(data, dict):
            # Response might be wrapped in a dictionary or be a single ticket
            if 'tickets' in data:
                tickets = data['tickets']
                if tickets and len(tickets) > 0:
                    ticket = tickets[0]
            else:
                # Single ticket object
                ticket = data
        
        # Enrich ticket with display names
        if ticket:
            return enrich_ticket_data(ticket)
        
        return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching tickets: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(f"Response type: {type(data)}")
        print(f"Response data: {data}")
        return None


def format_ticket_info(ticket):
    """
    Formats ticket information for display
    
    Args:
        ticket (dict): Ticket data from API
        
    Returns:
        str: Formatted ticket information
    """
    if not ticket:
        return "No open tickets found."
    
    ticket_info = f"""
╔══════════════════════════════════════════════════════════════
║ MOST RECENT OPEN TICKET
╠══════════════════════════════════════════════════════════════
║ Ticket ID:        {ticket.get('id', 'N/A')}
║ Subject:          {ticket.get('subject', 'N/A')}
║ 
║ Status:           {ticket.get('status_name', ticket.get('status', 'N/A'))}
║ Priority:         {ticket.get('priority_name', ticket.get('priority', 'N/A'))}
║ Source:           {ticket.get('source_name', ticket.get('source', 'N/A'))}
║ 
║ Requester:        {ticket.get('requester_id_name', ticket.get('requester_id', 'N/A'))}
║ Requested For:    {ticket.get('requested_for_id_name', ticket.get('requested_for_id', 'N/A'))}
║ Group:            {ticket.get('group_id_name', ticket.get('group_id', 'N/A'))}
║ Department:       {ticket.get('department_id_name', ticket.get('department_id', 'N/A'))}
║ Workspace:        {ticket.get('workspace_id_name', ticket.get('workspace_id', 'N/A'))}
║ 
║ Created At:       {ticket.get('created_at', 'N/A')}
║ Updated At:       {ticket.get('updated_at', 'N/A')}
║ 
║ Description:      {ticket.get('description_text', ticket.get('description', 'N/A'))[:80]}...
╚══════════════════════════════════════════════════════════════
"""
    return ticket_info


def main():
    """Main execution function"""
    print("Fetching most recent open ticket from FreshDesk...")
    print(f"Instance: {INSTANCE_URL}\n")
    
    ticket = get_recent_open_ticket()
    
    if ticket:
        print(format_ticket_info(ticket))
        print("\nFull ticket data:")
        import json
        print(json.dumps(ticket, indent=2))
    else:
        print("No open tickets found or error occurred.")


if __name__ == "__main__":
    main()
