#!/usr/bin/env python3
"""List all services in a Railway project."""

import os
import sys
from railway_deploy import RailwayClient

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv('.env')
except ImportError:
    pass

def main():
    if len(sys.argv) < 2:
        print("Usage: python list_services.py <project_id>")
        print("\nExample:")
        print("  python list_services.py 3bbb19eb-966f-4a33-8c62-98177ff91d40")
        sys.exit(1)
    
    project_id = sys.argv[1]
    
    # Get API token
    api_token = os.getenv("RAILWAY_TOKEN")
    if not api_token:
        print("Error: RAILWAY_TOKEN environment variable not set")
        sys.exit(1)
    
    try:
        client = RailwayClient(api_token)
        services = client.get_project_services(project_id)
        
        print(f"\nServices in project {project_id}:")
        print("=" * 60)
        if services:
            for service in services:
                print(f"Service ID: {service['id']}")
                print(f"  Name: {service['name']}")
                print()
        else:
            print("No services found in this project.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

