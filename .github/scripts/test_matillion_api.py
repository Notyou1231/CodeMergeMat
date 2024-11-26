# File: .github/scripts/test_matillion_api.py
import os
import requests
import json

def test_matillion_connection():
    # Get environment variables
    matillion_url = os.environ.get('MATILLION_URL', '').rstrip('/')
    api_key = os.environ.get('MATILLION_API_KEY', '')
    project_name = os.environ.get('MATILLION_PROJECT', '')

    # Print configuration (without sensitive data)
    print(f"Testing connection to: {matillion_url}")
    print(f"Project name: {project_name}")
    
    # Headers for API requests
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }

    try:
        # Test 1: Get Project Version
        print("\n1. Testing Project Version API...")
        version_url = f"{matillion_url}/rest/v1/group/project/{project_name}/version"
        version_response = requests.get(version_url, headers=headers)
        
        if version_response.status_code == 200:
            version_data = version_response.json()
            print("✅ Successfully got project version:", version_data['version'])
        else:
            print("❌ Failed to get project version")
            print(f"Status code: {version_response.status_code}")
            print(f"Response: {version_response.text}")
            return

        # Test 2: List Jobs
        print("\n2. Testing Jobs List API...")
        jobs_url = f"{matillion_url}/rest/v1/group/project/{project_name}/version/{version_data['version']}/jobs"
        jobs_response = requests.get(jobs_url, headers=headers)
        
        if jobs_response.status_code == 200:
            jobs = jobs_response.json()
            print("✅ Successfully retrieved jobs")
            print("\nFound Jobs:")
            for job in jobs:
                print(f"- {job['name']}")
        else:
            print("❌ Failed to list jobs")
            print(f"Status code: {jobs_response.status_code}")
            print(f"Response: {jobs_response.text}")
            return

        print("\n✅ All API tests passed successfully!")

    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        raise e

if __name__ == "__main__":
    test_matillion_connection()
