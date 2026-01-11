#!/usr/bin/env python3
"""
Railway API Automation Script

This script uses a workspace-level API token to:
1. Create a new Railway project
2. Deploy a Docker container/service to that project

Requirements:
- Python 3.7+
- requests library
- Railway workspace-level API token
"""

import os
import sys
import json
import requests
from typing import Optional, Dict, Any

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    # Load .env file from current directory (if it exists)
    # This must be called before any os.getenv() calls in main()
    env_loaded = load_dotenv('.env')
except ImportError:
    env_loaded = False
    # python-dotenv is optional, user can set env vars manually
except Exception:
    env_loaded = False


class RailwayClient:
    """Client for interacting with Railway's GraphQL API."""
    
    API_ENDPOINT = "https://backboard.railway.app/graphql/v2"
    
    def __init__(self, api_token: str):
        """
        Initialize the Railway API client.
        
        Args:
            api_token: Railway workspace-level API token
        """
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }
    
    def _make_request(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GraphQL request to Railway API.
        
        Args:
            query: GraphQL query/mutation string
            variables: Variables for the query/mutation
            
        Returns:
            JSON response from the API
            
        Raises:
            requests.HTTPError: If the request fails
            ValueError: If the response contains errors
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = requests.post(self.API_ENDPOINT, json=payload, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for GraphQL errors
        if "errors" in data:
            error_messages = [error.get("message", str(error)) for error in data["errors"]]
            raise ValueError(f"GraphQL errors: {', '.join(error_messages)}")
        
        return data
    
    def create_project(self, project_name: str, workspace_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new Railway project.
        
        Args:
            project_name: Name for the new project
            workspace_id: Optional workspace ID (if None, uses default workspace)
            
        Returns:
            Dictionary containing project ID and name
        """
        mutation = """
        mutation CreateProject($input: ProjectCreateInput!) {
            projectCreate(input: $input) {
                id
                name
            }
        }
        """
        
        variables = {
            "input": {
                "name": project_name,
            }
        }
        
        if workspace_id:
            variables["input"]["workspaceId"] = workspace_id
        
        result = self._make_request(mutation, variables)
        project = result["data"]["projectCreate"]
        
        print(f"✅ Project created: {project['name']} (ID: {project['id']})")
        return project
    
    def deploy_docker_image(
        self,
        project_id: str,
        docker_image: str,
        service_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deploy a Docker image as a service in a Railway project.
        
        Args:
            project_id: ID of the project to deploy to
            docker_image: Docker image name (e.g., 'kennethreitz/httpbin', 'nginx:latest')
            service_name: Optional name for the service (defaults to auto-generated name)
            
        Returns:
            Dictionary containing deployment information
        """
        # Try creating service with Docker image source directly
        # Railway's API might accept source during creation
        create_service_mutation = """
        mutation CreateService($input: ServiceCreateInput!) {
            serviceCreate(input: $input) {
                id
                name
                projectId
            }
        }
        """
        
        # Try format 1: Create service with image source (direct string)
        service_input = {
            "projectId": project_id,
            "source": {
                "image": docker_image
            }
        }
        
        if service_name:
            service_input["name"] = service_name
        
        create_service_variables = {"input": service_input}
        
        try:
            # Try creating service with source directly
            result = self._make_request(create_service_mutation, create_service_variables)
            service = result["data"]["serviceCreate"]
            service_id = service["id"]
            print(f"✅ Service created with Docker image: {service.get('name', 'Unnamed')} (ID: {service_id})")
            print(f"✅ Docker image '{docker_image}' configured successfully")
            print(f"⚠️  Note: Deployment should start automatically. Check Railway dashboard for status.")
            return service
        except ValueError as e:
            # If that fails, try creating service first, then updating
            print(f"⚠️  Direct source creation failed, trying alternative method...")
            
            # Create service without source
            service_input_minimal = {
                "projectId": project_id,
            }
            if service_name:
                service_input_minimal["name"] = service_name
            
            result = self._make_request(create_service_mutation, {"input": service_input_minimal})
            service = result["data"]["serviceCreate"]
            service_id = service["id"]
            print(f"✅ Service created: {service.get('name', 'Unnamed')} (ID: {service_id})")
            
            # Now try to update with source - try the simplest format first
            update_service_mutation = """
            mutation UpdateService($id: String!, $input: ServiceUpdateInput!) {
                serviceUpdate(id: $id, input: $input) {
                    id
                    name
                }
            }
            """
            
            # Format: Just the image string
            update_variables = {
                "id": service_id,
                "input": {
                    "source": {
                        "image": docker_image
                    }
                }
            }
            
            try:
                self._make_request(update_service_mutation, update_variables)
                print(f"✅ Service updated with Docker image: {docker_image}")
                print(f"⚠️  Note: Deployment should start automatically. Check Railway dashboard for status.")
            except ValueError as update_error:
                print(f"⚠️  Warning: Could not update service source: {update_error}")
                print(f"⚠️  You may need to configure the Docker image manually in Railway dashboard.")
                print(f"⚠️  Service ID: {service_id}")
            
            return service
            
        except ValueError as e:
            print(f"❌ Error during service deployment: {e}")
            raise
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """
        Get project information by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary containing project information
        """
        query = """
        query GetProject($id: String!) {
            project(id: $id) {
                id
                name
            }
        }
        """
        
        variables = {"id": project_id}
        result = self._make_request(query, variables)
        return result["data"]["project"]


def main():
    """Main function to create project and deploy Docker container."""
    
    # Get API token from environment variable
    api_token = os.getenv("RAILWAY_TOKEN")
    if not api_token:
        print("❌ Error: RAILWAY_TOKEN environment variable not set")
        print("\nPlease set your Railway workspace-level token:")
        print("\nOption 1: Create a .env file with:")
        print("  RAILWAY_TOKEN=your-token-here")
        print("\nOption 2: Set environment variable directly:")
        print("  export RAILWAY_TOKEN='your-token-here'  # Linux/Mac")
        print("  $env:RAILWAY_TOKEN='your-token-here'    # Windows PowerShell")
        sys.exit(1)
    
    # Configuration - can be overridden via environment variables
    project_name = os.getenv("RAILWAY_PROJECT_NAME", "My Docker Project")
    docker_image = os.getenv("RAILWAY_DOCKER_IMAGE", "kennethreitz/httpbin")
    service_name = os.getenv("RAILWAY_SERVICE_NAME")
    
    # Parse command line arguments if provided
    if len(sys.argv) > 1:
        project_name = sys.argv[1]
    if len(sys.argv) > 2:
        docker_image = sys.argv[2]
    if len(sys.argv) > 3:
        service_name = sys.argv[3]
    
    print("🚀 Railway Docker Deployment Script")
    print("=" * 50)
    print(f"Project Name: {project_name}")
    print(f"Docker Image: {docker_image}")
    if service_name:
        print(f"Service Name: {service_name}")
    print("=" * 50)
    
    try:
        # Initialize Railway client
        client = RailwayClient(api_token)
        
        # Create project
        print("\n📦 Creating project...")
        project = client.create_project(project_name)
        project_id = project["id"]
        
        # Deploy Docker container
        print(f"\n🐳 Deploying Docker image '{docker_image}'...")
        service = client.deploy_docker_image(
            project_id=project_id,
            docker_image=docker_image,
            service_name=service_name
        )
        
        print("\n" + "=" * 50)
        print("✅ Deployment Successful!")
        print("=" * 50)
        print(f"Project ID: {project_id}")
        print(f"Project Name: {project['name']}")
        print(f"Service ID: {service['id']}")
        print(f"Service Name: {service.get('name', 'N/A')}")
        print(f"\nView your project at: https://railway.app/project/{project_id}")
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

