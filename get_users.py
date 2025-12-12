#!/usr/bin/env python3
"""
FreshService Requesters Script
Lists all requesters (end users) who have access to FreshService
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


def display_requesters(requesters):
    """
    Display requesters in a formatted table
    
    Args:
        requesters (list): List of requesters
    """
    print("\n" + "="*100)
    print("FRESHSERVICE REQUESTERS REPORT")
    print("="*100)
    print(f"{'ID':<12} {'Name':<30} {'Email':<40} {'Active':<8}")
    print("-"*100)
    
    for requester in sorted(requesters, key=lambda x: x.get('first_name', '') or ''):
        req_id = requester.get('id') or 'N/A'
        first_name = requester.get('first_name') or ''
        last_name = requester.get('last_name') or ''
        name = f"{first_name} {last_name}".strip() or 'N/A'
        email = requester.get('primary_email') or 'N/A'
        active = 'Yes' if requester.get('active', False) else 'No'
        
        # Ensure all values are strings
        req_id_str = str(req_id)
        name_str = str(name)
        email_str = str(email)
        active_str = str(active)
        
        print(f"{req_id_str:<12} {name_str:<30} {email_str:<40} {active_str:<8}")
    
    # Summary
    print("\n" + "="*100)
    print("SUMMARY")
    print("="*100)
    active_requesters = sum(1 for r in requesters if r.get('active', False))
    
    print(f"Total Requesters:       {len(requesters):>6} (Active: {active_requesters})")
    print("="*100)


def save_to_json(requesters, filename=None):
    """
    Save requesters data to JSON file
    
    Args:
        requesters (list): List of requesters
        filename (str): Output filename (optional)
    """
    if filename is None:
        filename = f"freshservice_requesters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    data = {
        'generated_at': datetime.now().isoformat(),
        'requesters': requesters,
        'summary': {
            'total_requesters': len(requesters),
            'active_requesters': sum(1 for r in requesters if r.get('active', False))
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nData saved to: {filename}")


def save_to_csv(requesters):
    """
    Save requesters data to CSV file
    
    Args:
        requesters (list): List of requesters
    """
    import csv
    
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
    print("FreshService Requesters List")
    print("="*100)
    
    # Fetch all requesters
    requesters = fetch_all_requesters()
    
    # Display results
    display_requesters(requesters)
    
    # Ask to save
    print("\nExport Options:")
    print("  1. Save to JSON")
    print("  2. Save to CSV")
    print("  3. Both")
    print("  4. None")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == '1':
        save_to_json(requesters)
    elif choice == '2':
        save_to_csv(requesters)
    elif choice == '3':
        save_to_json(requesters)
        save_to_csv(requesters)
    else:
        print("\nNo export performed.")


if __name__ == "__main__":
    main()
