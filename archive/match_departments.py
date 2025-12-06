#!/usr/bin/env python3
"""
Script to match BU_Name from perimeters.csv with Name from departments.csv
and insert the matching ID into perimeters.csv
"""

import csv
from difflib import SequenceMatcher

def similarity(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_best_match(bu_name, departments, threshold=0.35):
    """
    Find the best matching department for a business unit name.
    Returns (dept_id, dept_name, score) or (None, None, 0) if no good match found.
    """
    best_match = None
    best_score = 0
    best_id = None
    
    bu_lower = bu_name.lower()
    
    # Special case mappings
    special_cases = {
        'asti - fort augustus': 'omexom mps - asti',
        've uk holding': 'vinci energies uk',
        'kigtek solutions': 'kigtek'
    }
    
    for key, value in special_cases.items():
        if key in bu_lower:
            for dept_id, dept_name in departments.items():
                if value in dept_name.lower():
                    return dept_id, dept_name, 1.0
    
    for dept_id, dept_name in departments.items():
        dept_lower = dept_name.lower()
        
        # Skip admin, projects, and other non-business unit departments
        if any(prefix in dept_lower for prefix in ['admin general', 'projects -', 'z do not use', 'central -']):
            continue
        
        # Calculate different matching strategies
        scores = []
        
        # 1. Direct substring match
        if bu_lower in dept_lower or dept_lower in bu_lower:
            scores.append(0.9)
        
        # 2. Check if key words from BU appear in department name
        bu_words = set(bu_lower.replace(',', '').replace('-', ' ').split())
        dept_words = set(dept_lower.replace(',', '').replace('-', ' ').split())
        
        # Remove common words
        common_words = {'desktop', '2026', 'central', 'network', 'the', 'and', 'of'}
        bu_words = bu_words - common_words
        dept_words = dept_words - common_words
        
        if bu_words and dept_words:
            word_overlap = len(bu_words & dept_words) / len(bu_words)
            scores.append(word_overlap)
        
        # 3. Overall string similarity
        scores.append(similarity(bu_name, dept_name))
        
        # Take the maximum score
        score = max(scores) if scores else 0
        
        if score > best_score:
            best_score = score
            best_match = dept_name
            best_id = dept_id
    
    if best_score >= threshold:
        return best_id, best_match, best_score
    return None, None, 0

def main():
    # Load departments
    departments = {}
    with open('departments.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dept_id = row['ID'].strip()
            dept_name = row['Name'].strip()
            departments[dept_id] = dept_name
    
    print(f"Loaded {len(departments)} departments\n")
    
    # Load perimeters and match
    perimeters_data = []
    with open('perimeters.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            perimeter = row['Perimeter'].strip()
            # The business unit name is currently in the BU_Id column
            bu_name = row.get('BU_Id', '').strip()
            
            if not bu_name:
                continue
            
            # Find best match
            dept_id, dept_name, score = find_best_match(bu_name, departments)
            
            perimeters_data.append({
                'Perimeter': perimeter,
                'BU_Id': dept_id or '',
                'BU_Name': bu_name,
                'matched_name': dept_name or 'NO MATCH',
                'score': score
            })
            
            status = '✓' if dept_id else '✗'
            print(f"{status} {bu_name}")
            if dept_id:
                print(f"  → ID: {dept_id} | {dept_name} (score: {score:.2f})")
            else:
                print(f"  → NO MATCH FOUND")
            print()
    
    # Write updated perimeters.csv
    with open('perimeters_updated.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Perimeter', 'BU_Id', 'BU_Name'])
        
        for row in perimeters_data:
            writer.writerow([row['Perimeter'], row['BU_Id'], row['BU_Name']])
    
    print("\n" + "="*70)
    print("Updated file saved as: perimeters_updated.csv")
    print("="*70)
    
    # Summary
    matched = sum(1 for row in perimeters_data if row['BU_Id'])
    total = len(perimeters_data)
    if total > 0:
        print(f"\nMatched: {matched}/{total} ({matched/total*100:.1f}%)")
    else:
        print("\nNo data processed")
        return
    
    unmatched = [row for row in perimeters_data if not row['BU_Id']]
    if unmatched:
        print(f"\nUnmatched business units ({len(unmatched)}):")
        for row in unmatched:
            print(f"  - {row['BU_Name']}")

if __name__ == "__main__":
    main()
