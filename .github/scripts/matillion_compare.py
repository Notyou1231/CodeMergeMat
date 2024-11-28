import json
import sys
import os
from typing import Dict, List, Tuple

class MatillionJobAnalyzer:
    def __init__(self, old_file_path: str, new_file_path: str):
        self.old_file_path = old_file_path
        self.new_file_path = new_file_path
        
    def read_json_file(self, file_path: str) -> Dict:
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return {}
            
    def analyze_changes(self) -> Dict:
        old_job = self.read_json_file(self.old_file_path)
        new_job = self.read_json_file(self.new_file_path)
        
        changes = {
            'components': {'added': [], 'modified': [], 'removed': []},
            'variables': {'modified': []},
            'info_changes': {'modified': []},
            'total_changes': 0
        }
        
        # Compare job info
        old_info = old_job.get('info', {})
        new_info = new_job.get('info', {})
        
        # Specifically check for name changes
        if old_info.get('name') != new_info.get('name'):
            changes['info_changes']['modified'].append({
                'type': 'name',
                'old': old_info.get('name', 'Unknown'),
                'new': new_info.get('name', 'Unknown')
            })
        
        # Compare other info changes
        for key in set(old_info.keys()) | set(new_info.keys()):
            if key != 'name' and old_info.get(key) != new_info.get(key):
                changes['info_changes']['modified'].append({
                    'type': key,
                    'old': old_info.get(key, 'Not present'),
                    'new': new_info.get(key, 'Not present')
                })
        
        # Calculate total changes
        changes['total_changes'] = (
            len(changes['components']['added']) +
            len(changes['components']['modified']) +
            len(changes['components']['removed']) +
            len(changes['variables']['modified']) +
            len(changes['info_changes']['modified'])
        )
        
        return changes

    def print_report(self, changes: Dict):
        file_name = os.path.basename(self.new_file_path)
        print(f"File: {file_name}\n")
        print(f"Total Component Changes: {len(changes['components']['added']) + len(changes['components']['modified']) + len(changes['components']['removed'])}")
        print(f"Total Variable Changes: {len(changes['variables']['modified'])}")
        print(f"Total Info Changes: {len(changes['info_changes']['modified'])}")
        print(f"Changes Detected: {'Yes' if changes['total_changes'] > 0 else 'No'}")
        
        if changes['total_changes'] > 0:
            print("\nChanges Summary:")
            
            # Print info changes
            for idx, change in enumerate(changes['info_changes']['modified'], 1):
                if change['type'] == 'name':
                    print(f"{idx}. Job Name Changed:")
                    print(f"   - From: {change['old']}")
                    print(f"   - To:   {change['new']}")
                else:
                    print(f"{idx}. {change['type'].title()} Changed:")
                    print(f"   - From: {change['old']}")
                    print(f"   - To:   {change['new']}")
            
            # Print other changes if present
            current_idx = len(changes['info_changes']['modified']) + 1
            
            if changes['components']['added']:
                for comp in changes['components']['added']:
                    print(f"{current_idx}. Component Added: {comp['name']}")
                    current_idx += 1
            
            if changes['components']['modified']:
                for comp in changes['components']['modified']:
                    print(f"{current_idx}. Component Modified: {comp['name']}")
                    current_idx += 1
            
            if changes['components']['removed']:
                for comp in changes['components']['removed']:
                    print(f"{current_idx}. Component Removed: {comp['name']}")
                    current_idx += 1
            
            if changes['variables']['modified']:
                for var in changes['variables']['modified']:
                    print(f"{current_idx}. Variable Changed: {var['name']}")
                    print(f"   - From: {var['old_value']}")
                    print(f"   - To:   {var['new_value']}")
                    current_idx += 1

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <old_file_path> <new_file_path>")
        sys.exit(1)
    
    old_file = sys.argv[1]
    new_file = sys.argv[2]
    analyzer = MatillionJobAnalyzer(old_file, new_file)
    changes = analyzer.analyze_changes()
    analyzer.print_report(changes)
