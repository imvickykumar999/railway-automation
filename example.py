#!/usr/bin/env python3
"""
Example usage of the RailwayClient class

This script demonstrates how to use the RailwayClient class
directly in your own Python code.
"""

import os
from railway_deploy import RailwayClient


def example_basic_deployment():
    """Basic example: Create project and deploy a Docker image."""
    
    # Initialize client with your token
    token = os.getenv("RAILWAY_TOKEN")
    if not token:
        print("Please set RAILWAY_TOKEN environment variable")
        return
    
    client = RailwayClient(token)
    
    # Create a project
    project = client.create_project("Example Project")
    project_id = project["id"]
    
    # Deploy a Docker image
    service = client.deploy_docker_image(
        project_id=project_id,
        docker_image="nginx:latest",
        service_name="web-server"
    )
    
    print(f"Deployed service: {service['id']}")


def example_multiple_services():
    """Example: Create project and deploy multiple services."""
    
    token = os.getenv("RAILWAY_TOKEN")
    if not token:
        print("Please set RAILWAY_TOKEN environment variable")
        return
    
    client = RailwayClient(token)
    
    # Create project
    project = client.create_project("Multi-Service Project")
    project_id = project["id"]
    
    # Deploy multiple services
    services = [
        ("nginx:latest", "web-server"),
        ("redis:alpine", "cache"),
        ("postgres:15", "database"),
    ]
    
    for image, name in services:
        service = client.deploy_docker_image(
            project_id=project_id,
            docker_image=image,
            service_name=name
        )
        print(f"✅ Deployed {name}: {service['id']}")


if __name__ == "__main__":
    print("Running basic deployment example...")
    example_basic_deployment()
    
    # Uncomment to run multiple services example:
    # example_multiple_services()

