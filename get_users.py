#!/usr/bin/env python3
"""
FreshService Users Script
Lists all users (requesters and agents) who have access to FreshService
"""

import requests
import json
from datetime import datetime


# Configuration
INSTANCE_URL = "axiansnetworkltd.freshservice.com"
API_KEY = "kGALZPRyHlTmnvDEmnuh"
API_BASE_URL = f"https://{INSTANCE_URL}/api/v2"


def fetch_all_requesters():
    """
    Fetch all requesters from FreshService
    
    Returns:
        list: List of requester dictionaries
    """
    auth = (API_KEY, 'X')
    headers = {'Content-Type': 'application/json'}
    
    all_requesters = []
    page = 1
    per_page = 100
    max_pages = 100  # Safety limit
    
    print("Fetching requesters...")
    
    while page <= max_pages:
        url = f"{API_BASE_URL}/requesters"
        params = {'per_page': per_page, 'page': page}
        
        try:
            response = requests.get(url, auth=auth, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Handle both list and dict responses
            requesters = data if isinstance(data, list) else data.get('requesters', [])
            
            if not requesters:
                break
            
            all_requesters.extend(requesters)
            print(f"  Page {page}: Retrieved {len(requesters)} requesters (Total: {len(all_requesters)})")
            
            # Check if there are more pages
            if len(requesters) < per_page:
                break
            
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching requesters on page {page}: {e}")
            break
    
    return all_requesters


def fetch_all_agents():
    """
    Fetch all agents from FreshService
    
    Returns:
        list: List of agent dictionaries
    """
    auth = (API_KEY, 'X')
    headers = {'Content-Type': 'application/json'}
    
    all_agents = []
    page = 1
    per_page = 100
    max_pages = 100  # Safety limit
    
    print("\nFetching agents...")
    
    while page <= max_pages:
        url = f"{API_BASE_URL}/agents"
        params = {'per_page': per_page, 'page': page}
        
        try:
            response = requests.get(url, auth=auth, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Handle both list and dict responses
            agents = data if isinstance(data, list) else data.get('agents', [])
            
            if not agents:
                break
            
            all_agents.extend(agents)
            print(f"  Page {page}: Retrieved {len(agents)} agents (Total: {len(all_agents)})")
            
            # Check if there are more pages
            if len(agents) < per_page:
                break
            
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching agents on page {page}: {e}")
            break
    
    return all_agents


def display_users(requesters, agents):
    """
    Display users in a formatted table
    
    Args:
        requesters (list): List of requesters
        agents (list): List of agents
    """
    print("\n" + "="*100)
    print("FRESHSERVICE USERS REPORT")
    print("="*100)
    
    # Display Agents
    print("\n" + "-"*100)
    print(f"AGENTS ({len(agents)})")
    print("-"*100)
    print(f"{'ID':<12} {'Name':<30} {'Email':<40} {'Active':<8}")
    print("-"*100)
    
    for agent in sorted(agents, key=lambda x: x.get('first_name', '') or ''):
        agent_id = agent.get('id', 'N/A')
        first_name = agent.get('first_name', '')
        last_name = agent.get('last_name', '')
        name = f"{first_name} {last_name}".strip() or 'N/A'
        email = agent.get('email', 'N/A')
        active = 'Yes' if agent.get('active', False) else 'No'
        
        print(f"{agent_id:<12} {name:<30} {email:<40} {active:<8}")
    
    # Display Requesters
    print("\n" + "-"*100)
    print(f"REQUESTERS ({len(requesters)})")
    print("-"*100)
    print(f"{'ID':<12} {'Name':<30} {'Email':<40} {'Active':<8}")
    print("-"*100)
    
    for requester in sorted(requesters, key=lambda x: x.get('first_name', '') or ''):
        req_id = requester.get('id', 'N/A')
        first_name = requester.get('first_name', '')
        last_name = requester.get('last_name', '')
        name = f"{first_name} {last_name}".strip() or 'N/A'
        email = requester.get('primary_email', 'N/A')
        active = 'Yes' if requester.get('active', False) else 'No'
        
        print(f"{req_id:<12} {name:<30} {email:<40} {active:<8}")
    
    # Summary
    print("\n" + "="*100)
    print("SUMMARY")
    print("="*100)
    active_agents = sum(1 for a in agents if a.get('active', False))
    active_requesters = sum(1 for r in requesters if r.get('active', False))
    
    print(f"Total Agents:           {len(agents):>6} (Active: {active_agents})")
    print(f"Total Requesters:       {len(requesters):>6} (Active: {active_requesters})")
    print(f"Total Users:            {len(agents) + len(requesters):>6}")
    print("="*100)


def save_to_json(requesters, agents, filename=None):
    """
    Save users data to JSON file
    
    Args:
        requesters (list): List of requesters
        agents (list): List of agents
        filename (str): Output filename (optional)
    """
    if filename is None:
        filename = f"freshservice_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    data = {
        'generated_at': datetime.now().isoformat(),
        'agents': agents,
        'requesters': requesters,
        'summary': {
            'total_agents': len(agents),
            'total_requesters': len(requesters),
            'total_users': len(agents) + len(requesters),
            'active_agents': sum(1 for a in agents if a.get('active', False)),
            'active_requesters': sum(1 for r in requesters if r.get('active', False))
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nData saved to: {filename}")


def save_to_csv(requesters, agents):
    """
    Save users data to CSV files
    
    Args:
        requesters (list): List of requesters
        agents (list): List of agents
    """
    import csv
    
    # Save agents
    agents_file = f"freshservice_agents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(agents_file, 'w', encoding='utf-8', newline='') as f:
        if agents:
            # Get all unique keys
            fieldnames = ['id', 'first_name', 'last_name', 'email', 'active', 'job_title', 
                         'department_ids', 'created_at', 'updated_at']
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(agents)
    print(f"Agents saved to: {agents_file}")
    
    # Save requesters
    requesters_file = f"freshservice_requesters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(requesters_file, 'w', encoding='utf-8', newline='') as f:
        if requesters:
            fieldnames = ['id', 'first_name', 'last_name', 'primary_email', 'active', 
                         'job_title', 'department_ids', 'created_at', 'updated_at']
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(requesters)
    print(f"Requesters saved to: {requesters_file}")


def main():
    """Main execution function"""
    print("FreshService Users List")
    print("="*100)
    
    # Fetch all users
    requesters = fetch_all_requesters()
    agents = fetch_all_agents()
    
    # Display results
    display_users(requesters, agents)
    
    # Ask to save
    print("\nExport Options:")
    print("  1. Save to JSON")
    print("  2. Save to CSV")
    print("  3. Both")
    print("  4. None")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == '1':
        save_to_json(requesters, agents)
    elif choice == '2':
        save_to_csv(requesters, agents)
    elif choice == '3':
        save_to_json(requesters, agents)
        save_to_csv(requesters, agents)
    else:
        print("\nNo export performed.")


if __name__ == "__main__":
    main()
