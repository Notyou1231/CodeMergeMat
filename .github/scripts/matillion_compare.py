import json
import sys
import os

class MatillionJobAnalyzer:
    def __init__(self, old_file_path: str, new_file_path: str):
        self.old_file_path = old_file_path
        self.new_file_path = new_file_path
        
    def read_json_file(self, file_path: str) -> dict:
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return {}
            
    def get_tables_from_component(self, component: dict) -> dict:
        tables = {
            'source': [],
            'target': []
        }
        
        # Extract source and target tables from parameters
        parameters = component.get('parameters', {})
        for param in parameters.values():
            if isinstance(param, dict):
                elements = param.get('elements', {})
                for element in elements.values():
                    values = element.get('values', {})
                    for value in values.values():
                        if isinstance(value, dict):
                            val = value.get('value', '')
                            if 'Source Table Name' in param.get('name', ''):
                                tables['source'].append(val)
                            elif 'Target Table Name' in param.get('name', ''):
                                tables['target'].append(val)
        
        return tables

    def analyze_changes(self) -> dict:
        old_job = self.read_json_file(self.old_file_path)
        new_job = self.read_json_file(self.new_file_path)
        
        changes = {
            'job_name_changes': [],
            'component_changes': [],
            'table_changes': [],
            'total_changes': 0
        }
        
        # Check job name changes
        if old_job.get('info', {}).get('name') != new_job.get('info', {}).get('name'):
            changes['job_name_changes'].append({
                'type': 'job_name',
                'old': old_job.get('info', {}).get('name'),
                'new': new_job.get('info', {}).get('name')
            })

        # Compare components and their tables
        old_components = old_job.get('job', {}).get('components', {})
        new_components = new_job.get('job', {}).get('components', {})
        
        for comp_id, new_comp in new_components.items():
            old_comp = old_components.get(comp_id)
            if not old_comp:
                # New component added
                changes['component_changes'].append({
                    'type': 'added',
                    'name': self.get_component_name(new_comp),
                    'tables': self.get_tables_from_component(new_comp)
                })
            else:
                # Compare existing component
                old_tables = self.get_tables_from_component(old_comp)
                new_tables = self.get_tables_from_component(new_comp)
                
                if old_tables != new_tables:
                    changes['table_changes'].append({
                        'component': self.get_component_name(new_comp),
                        'old_tables': old_tables,
                        'new_tables': new_tables
                    })

        changes['total_changes'] = (
            len(changes['job_name_changes']) +
            len(changes['component_changes']) +
            len(changes['table_changes'])
        )
        
        return changes

    def get_component_name(self, component: dict) -> str:
        try:
            return component.get('parameters', {}).get('1', {}).get('elements', {}).get('1', {}).get('values', {}).get('1', {}).get('value', 'Unnamed')
        except:
            return 'Unnamed Component'

    def print_report(self):
        changes = self.analyze_changes()
        
        print(f"File: {os.path.basename(self.new_file_path)}")
        print(f"Total Changes: {changes['total_changes']}")
        print(f"Changes Detected: {'Yes' if changes['total_changes'] > 0 else 'No'}\n")
        
        if changes['total_changes'] > 0:
            print("Changes Summary:")
            
            # Print job name changes
            for change in changes['job_name_changes']:
                print("\nJob Name Changed:")
                print(f"  From: {change['old']}")
                print(f"  To:   {change['new']}")
            
            # Print component changes
            for change in changes['component_changes']:
                print(f"\nComponent {change['type'].title()}:")
                print(f"  Name: {change['name']}")
                if change['tables']['source'] or change['tables']['target']:
                    print("  Tables:")
                    print("    Source:", ', '.join(change['tables']['source']) or 'None')
                    print("    Target:", ', '.join(change['tables']['target']) or 'None')
            
            # Print table changes
            for change in changes['table_changes']:
                print(f"\nTable Changes in Component '{change['component']}':")
                print("  Source Tables:")
                print("    Old:", ', '.join(change['old_tables']['source']) or 'None')
                print("    New:", ', '.join(change['new_tables']['source']) or 'None')
                print("  Target Tables:")
                print("    Old:", ', '.join(change['old_tables']['target']) or 'None')
                print("    New:", ', '.join(change['new_tables']['target']) or 'None')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <old_file_path> <new_file_path>")
        sys.exit(1)
    
    analyzer = MatillionJobAnalyzer(sys.argv[1], sys.argv[2])
    analyzer.print_report()
