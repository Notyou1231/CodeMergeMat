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
        # Read both files
        old_job = self.read_json_file(self.old_file_path)
        new_job = self.read_json_file(self.new_file_path)
        
        # Initialize change tracking
        changes = {
            'components': {'added': [], 'modified': [], 'removed': []},
            'variables': {'modified': []},
            'connectors': {'modified': []},
            'total_changes': 0
        }
        
        # Compare components
        old_components = old_job.get('job', {}).get('components', {})
        new_components = new_job.get('job', {}).get('components', {})
        
        # Check for added and modified components
        for comp_id, comp in new_components.items():
            if comp_id not in old_components:
                changes['components']['added'].append({
                    'id': comp_id,
                    'name': self.get_component_name(comp),
                    'type': comp.get('executionHint', 'Unknown')
                })
            elif comp != old_components[comp_id]:
                changes['components']['modified'].append({
                    'id': comp_id,
                    'name': self.get_component_name(comp),
                    'type': comp.get('executionHint', 'Unknown'),
                    'old_values': old_components[comp_id],
                    'new_values': comp
                })
        
        # Check for removed components
        for comp_id, comp in old_components.items():
            if comp_id not in new_components:
                changes['components']['removed'].append({
                    'id': comp_id,
                    'name': self.get_component_name(comp),
                    'type': comp.get('executionHint', 'Unknown')
                })
        
        # Compare variables
        old_vars = old_job.get('job', {}).get('variables', {})
        new_vars = new_job.get('job', {}).get('variables', {})
        
        for var_name, new_var in new_vars.items():
            if var_name not in old_vars or new_var != old_vars[var_name]:
                changes['variables']['modified'].append({
                    'name': var_name,
                    'old_value': old_vars.get(var_name, {}).get('value', 'Not Found'),
                    'new_value': new_var.get('value')
                })
        
        # Calculate total changes
        changes['total_changes'] = (
            len(changes['components']['added']) +
            len(changes['components']['modified']) +
            len(changes['components']['removed']) +
            len(changes['variables']['modified'])
        )
        
        return changes

    def get_component_name(self, component: Dict) -> str:
        try:
            return component.get('parameters', {}).get('1', {}).get('elements', {}).get('1', {}).get('values', {}).get('1', {}).get('value', 'Unnamed')
        except:
            return 'Unnamed Component'

    def print_report(self, changes: Dict):
        print(f"File: {os.path.basename(self.new_file_path)}")
        print(f"Total Component Changes: {len(changes['components']['added']) + len(changes['components']['modified']) + len(changes['components']['removed'])}")
        print(f"Total Variable Changes: {len(changes['variables']['modified'])}")
        print(f"Changes Detected: {'Yes' if changes['total_changes'] > 0 else 'No'}")
        
        if changes['total_changes'] > 0:
            print("\nNew Changes Detected:")
            change_count = 1
            
            # Print added components
            for comp in changes['components']['added']:
                print(f"{change_count}. New Component Added:")
                print(f"   Name: {comp['name']}")
                print(f"   Type: {comp['type']}")
                change_count += 1
            
            # Print modified components
            for comp in changes['components']['modified']:
                print(f"{change_count}. Component Modified:")
                print(f"   Name: {comp['name']}")
                print(f"   Type: {comp['type']}")
                change_count += 1
            
            # Print removed components
            for comp in changes['components']['removed']:
                print(f"{change_count}. Component Removed:")
                print(f"   Name: {comp['name']}")
                print(f"   Type: {comp['type']}")
                change_count += 1
            
            # Print variable changes
            for var in changes['variables']['modified']:
                print(f"{change_count}. Variable Changed:")
                print(f"   Name: {var['name']}")
                print(f"   Old Value: {var['old_value']}")
                print(f"   New Value: {var['new_value']}")
                change_count += 1

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <old_file_path> <new_file_path>")
        sys.exit(1)
    
    old_file = sys.argv[1]
    new_file = sys.argv[2]
    
    # Create analyzer instance
    analyzer = MatillionJobAnalyzer(old_file, new_file)
    
    # Analyze changes
    changes = analyzer.analyze_changes()
    
    # Print report
    analyzer.print_report(changes)

if __name__ == "__main__":
    main()
