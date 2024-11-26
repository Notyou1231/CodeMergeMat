# File: .github/scripts/test_matillion_api.py
import os
import requests
import json
import sys

def test_matillion_connection():
    # Get environment variables and validate them
    matillion_url = os.environ.get('MATILLION_URL', '').rstrip('/')
    api_key = os.environ.get('MATILLION_API_KEY', '')
    project_name = os.environ.get('MATILLION_PROJECT', '')

    # Validate required environment variables
    if not all([matillion_url, api_key, project_name]):
        print("❌ Error: Missing required environment variables")
        print(f"MATILLION_URL: {'Set' if matillion_url else 'Missing'}")
        print(f"MATILLION_API_KEY: {'Set' if api_key else 'Missing'}")
        print(f"MATILLION_PROJECT: {'Set' if project_name else 'Missing'}")
        sys.exit(1)

    # Print configuration (masking sensitive data)
    print(f"Testing connection to: {matillion_url}")
    print(f"Project name: {project_name}")
    print(f"API Key (first 4 chars): {api_key[:4]}***")
    
    # Headers for API requests
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        # Test 1: Simple API health check
        print("\n1. Testing API Health...")
        health_url = f"{matillion_url}/rest/v1/group/me"
        health_response = requests.get(health_url, headers=headers)
        
        if health_response.status_code != 200:
            print("❌ API Health check failed")
            print(f"Status code: {health_response.status_code}")
            print("Response:", health_response.text[:200])  # Show first 200 chars
            return

        print("✅ API Health check passed")

        # Test 2: Get Project Version
        print("\n2. Testing Project Version API...")
        version_url = f"{matillion_url}/rest/v1/group/project/{project_name}/version"
        print(f"Making request to: {version_url}")
        
        version_response = requests.get(version_url, headers=headers)
        print(f"Response status: {version_response.status_code}")
        print(f"Response headers: {dict(version_response.headers)}")
        
        try:
            response_text = version_response.text
            print(f"Raw response: {response_text[:200]}")  # Show first 200 chars
            version_data = version_response.json()
            print("✅ Successfully got project version:", version_data.get('version', 'N/A'))
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {str(e)}")
            print(f"Raw response: {response_text[:200]}")
            return

        # Test 3: List Jobs
        print("\n3. Testing Jobs List API...")
        version = version_data.get('version', '1')  # Default to '1' if not found
        jobs_url = f"{matillion_url}/rest/v1/group/project/{project_name}/version/{version}/jobs"
        print(f"Making request to: {jobs_url}")
        
        jobs_response = requests.get(jobs_url, headers=headers)
        print(f"Response status: {jobs_response.status_code}")
        
        try:
            jobs = jobs_response.json()
            print("✅ Successfully retrieved jobs")
            print("\nFound Jobs:")
            for job in jobs:
                print(f"- {job.get('name', 'Unnamed Job')}")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse jobs JSON: {str(e)}")
            print(f"Raw response: {jobs_response.text[:200]}")
            return

        print("\n✅ All API tests passed successfully!")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Connection error: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text[:200]}")
        raise e
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        raise e

if __name__ == "__main__":
    test_matillion_connection()
