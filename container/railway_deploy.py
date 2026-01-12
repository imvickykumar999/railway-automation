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
            error_details = ', '.join(error_messages)
            # Also include the full error for debugging
            if hasattr(response, 'text'):
                error_details += f" | Response: {response.text}"
            raise ValueError(f"GraphQL errors: {error_details}")
        
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
    
    def get_project_services(self, project_id: str) -> list:
        """
        Get all services in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of services
        """
        query = """
        query GetProjectServices($projectId: String!) {
            project(id: $projectId) {
                services {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
        
        variables = {"projectId": project_id}
        result = self._make_request(query, variables)
        services = result["data"]["project"]["services"]["edges"]
        return [edge["node"] for edge in services]
    
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
    
    def get_service_logs(
        self,
        service_id: str,
        limit: int = 100
    ) -> list:
        """
        Get logs for a service's latest deployment.
        
        Note: Railway's GraphQL API may not support direct log queries.
        This method attempts to fetch logs but may return empty if not supported.
        
        Args:
            service_id: Service ID
            limit: Maximum number of log entries to retrieve (default: 100)
            
        Returns:
            List of log entries, each containing message, timestamp, and level
        """
        # Railway's GraphQL API doesn't appear to support direct log queries
        # Logs are typically accessed via the Railway dashboard or CLI
        # Return empty list to indicate logs are not available via API
        print(f"Warning: Railway GraphQL API does not support direct log queries. Logs can be viewed at https://railway.app")
        return []
    
    def set_environment_variables(
        self,
        service_id: str,
        environment_variables: Dict[str, str],
        environment_name: str = "production"
    ) -> bool:
        """
        Set environment variables for a service.
        
        Args:
            service_id: Service ID
            environment_variables: Dictionary of variable names to values
            environment_name: Environment name (default: "production")
            
        Returns:
            True if successful, False otherwise
        """
        # First, get the service to find the project and environment
        get_service_query = """
        query GetService($id: String!) {
            service(id: $id) {
                id
                projectId
            }
        }
        """
        
        try:
            service_result = self._make_request(get_service_query, {"id": service_id})
            project_id = service_result["data"]["service"]["projectId"]
            
            # Get environment ID - Railway uses connection pattern
            get_env_query = """
            query GetEnvironment($projectId: String!) {
                environments(projectId: $projectId) {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
            """
            
            env_result = self._make_request(get_env_query, {
                "projectId": project_id
            })
            
            # Extract environments from connection
            edges = env_result["data"]["environments"]["edges"]
            environments = [edge["node"] for edge in edges]
            
            # Find the environment with matching name
            environment = None
            for env in environments:
                if env.get("name") == environment_name:
                    environment = env
                    break
            
            if not environment:
                # If environment not found, use the first one or create it
                if environments:
                    environment = environments[0]
                    print(f"Warning: Environment '{environment_name}' not found, using '{environment['name']}'")
                else:
                    print(f"Error: No environments found for project")
                    return False
            
            environment_id = environment["id"]
            
            # Set environment variables using variableUpsert (one at a time)
            upsert_mutation = """
            mutation UpsertVariable($input: VariableUpsertInput!) {
                variableUpsert(input: $input)
            }
            """
            
            # Set each variable individually
            # Railway requires projectId, environmentId, and serviceId for service-level variables
            for name, value in environment_variables.items():
                # Use all three IDs for service-level variables
                variable_input = {
                    "projectId": project_id,
                    "environmentId": environment_id,
                    "serviceId": service_id,
                    "name": name,
                    "value": value
                }
                
                try:
                    self._make_request(upsert_mutation, {"input": variable_input})
                except (ValueError, requests.exceptions.HTTPError) as e:
                    # If that fails, try without serviceId (project-level variable)
                    variable_input = {
                        "projectId": project_id,
                        "environmentId": environment_id,
                        "name": name,
                        "value": value
                    }
                    try:
                        self._make_request(upsert_mutation, {"input": variable_input})
                        print(f"  Warning: Set {name} as project-level variable (not service-specific)")
                    except (ValueError, requests.exceptions.HTTPError) as e2:
                        error_details = str(e2)
                        if hasattr(e2, 'response') and hasattr(e2.response, 'text'):
                            error_details = e2.response.text
                        raise ValueError(f"Failed to set {name}: {error_details}")
            
            print(f"[OK] Set {len(environment_variables)} environment variable(s)")
            for name in environment_variables.keys():
                print(f"   - {name}")
            
            return True
            
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                error_details = e.response.text
                try:
                    import json
                    error_json = json.loads(error_details)
                    if "errors" in error_json:
                        error_msg = "; ".join([err.get("message", str(err)) for err in error_json["errors"]])
                except:
                    error_msg = error_details
            print(f"Warning: Could not set environment variables: {error_msg}")
            print(f"   You may need to set them manually in Railway dashboard")
            return False
        except ValueError as e:
            print(f"Warning: Could not set environment variables: {e}")
            print(f"   You may need to set them manually in Railway dashboard")
            return False
        except Exception as e:
            print(f"Warning: Unexpected error: {e}")
            print(f"   You may need to set them manually in Railway dashboard")
            return False


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
    
    # Environment variables to set for the service (from .env file)
    service_env_vars = {}
    stream_key = os.getenv("STREAM_KEY")
    youtube_id = os.getenv("YouTube_ID") or os.getenv("YOUTUBE_ID")
    
    if stream_key:
        service_env_vars["STREAM_KEY"] = stream_key
    if youtube_id:
        service_env_vars["YouTube_ID"] = youtube_id
    
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
        service_id = service["id"]
        
        # Set environment variables if provided
        if service_env_vars:
            print(f"\n🔧 Setting environment variables...")
            client.set_environment_variables(
                service_id=service_id,
                environment_variables=service_env_vars
            )
            print(f"⚠️  Note: Service will automatically redeploy with new environment variables.")
        
        print("\n" + "=" * 50)
        print("✅ Deployment Successful!")
        print("=" * 50)
        print(f"Project ID: {project_id}")
        print(f"Project Name: {project['name']}")
        print(f"Service ID: {service_id}")
        print(f"Service Name: {service.get('name', 'N/A')}")
        if service_env_vars:
            print(f"\nEnvironment Variables Set:")
            for key in service_env_vars.keys():
                print(f"  - {key}")
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

