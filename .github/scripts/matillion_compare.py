import json
import sys
import os

class MatillionJobAnalyzer:
    def __init__(self, old_file_path: str, new_file_path: str):
        self.old_file_path = old_file_path
        self.new_file_path = new_file_path
        
    def read_json_file(self, file_path: str):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            return {}
            
    def analyze_changes(self):
        old_job = self.read_json_file(self.old_file_path)
        new_job = self.read_json_file(self.new_file_path)
        
        changes = {
            'info_changes': [],
            'component_changes': 0,
            'variable_changes': 0
        }
        
        # Compare job info name
        old_name = old_job.get('info', {}).get('name', '')
        new_name = new_job.get('info', {}).get('name', '')
        
        if old_name != new_name:
            changes['info_changes'].append({
                'old_name': old_name,
                'new_name': new_name
            })
        
        return changes

    def print_report(self, changes):
        # Print simple stats
        print(f"File: {os.path.basename(self.new_file_path)}")
        print(f"Total Component Changes: {changes['component_changes']}")
        print(f"Total Variable Changes: {changes['variable_changes']}")
        print(f"Total Info Changes: {len(changes['info_changes'])}")
        print(f"Changes Detected: {'Yes' if changes['info_changes'] else 'No'}")
        
        if changes['info_changes']:
            print("\nChanges Summary:")
            for idx, change in enumerate(changes['info_changes'], 1):
                print(f"{idx}. Job Name Changed:")
                print(f"   - From: {change['old_name']}")
                print(f"   - To:   {change['new_name']}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <old_file_path> <new_file_path>")
        sys.exit(1)
    
    analyzer = MatillionJobAnalyzer(sys.argv[1], sys.argv[2])
    changes = analyzer.analyze_changes()
    analyzer.print_report(changes)
