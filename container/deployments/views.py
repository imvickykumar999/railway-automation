import os
import sys
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import RailwayDeployment
from .forms import RailwayDeploymentForm

# Import RailwayClient from the parent directory (railway-automation root)
# views.py is at: container/deployments/views.py
# railway_deploy.py is at: railway_deploy.py (root)
container_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, container_dir)
try:
    from railway_deploy import RailwayClient
except ImportError:
    RailwayClient = None


def deployment_form(request):
    """Handle the deployment configuration form."""
    if request.method == 'POST':
        form = RailwayDeploymentForm(request.POST)
        if form.is_valid():
            deployment = form.save()
            messages.success(
                request,
                f'Deployment configuration "{deployment.project_name}" saved successfully!'
            )
            return redirect('deployments:deployment_list')
    else:
        form = RailwayDeploymentForm()
    
    return render(request, 'deployments/form.html', {'form': form})


def deployment_list(request):
    """Display list of all deployment configurations."""
    deployments = RailwayDeployment.objects.all()
    return render(request, 'deployments/list.html', {'deployments': deployments})


def deployment_detail(request, pk):
    """Display details of a specific deployment configuration."""
    try:
        deployment = RailwayDeployment.objects.get(pk=pk)
    except RailwayDeployment.DoesNotExist:
        messages.error(request, 'Deployment configuration not found.')
        return redirect('deployments:deployment_list')
    
    return render(request, 'deployments/detail.html', {'deployment': deployment})


def deployment_edit(request, pk):
    """Edit an existing deployment configuration."""
    try:
        deployment = RailwayDeployment.objects.get(pk=pk)
    except RailwayDeployment.DoesNotExist:
        messages.error(request, 'Deployment configuration not found.')
        return redirect('deployments:deployment_list')
    
    if request.method == 'POST':
        form = RailwayDeploymentForm(request.POST, instance=deployment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Deployment configuration updated successfully!')
            return redirect('deployments:deployment_detail', pk=pk)
    else:
        form = RailwayDeploymentForm(instance=deployment)
    
    return render(request, 'deployments/form.html', {'form': form, 'deployment': deployment})


def deployment_delete(request, pk):
    """Delete a deployment configuration."""
    try:
        deployment = RailwayDeployment.objects.get(pk=pk)
        if request.method == 'POST':
            deployment.delete()
            messages.success(request, 'Deployment configuration deleted successfully!')
            return redirect('deployments:deployment_list')
    except RailwayDeployment.DoesNotExist:
        messages.error(request, 'Deployment configuration not found.')
        return redirect('deployments:deployment_list')
    
    return render(request, 'deployments/delete.html', {'deployment': deployment})


def deployment_deploy(request, pk):
    """Deploy the configuration to Railway."""
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('deployments:deployment_detail', pk=pk)
    
    try:
        deployment = RailwayDeployment.objects.get(pk=pk)
    except RailwayDeployment.DoesNotExist:
        messages.error(request, 'Deployment configuration not found.')
        return redirect('deployments:deployment_list')
    
    if RailwayClient is None:
        messages.error(request, 'Railway deployment module not found. Please ensure railway_deploy.py is available.')
        return redirect('deployments:deployment_detail', pk=pk)
    
    try:
        # Initialize Railway client
        client = RailwayClient(deployment.railway_token)
        
        # Check if this deployment already has a project_id (redeploy scenario)
        if deployment.railway_project_id and deployment.railway_service_id:
            # Redeploy to existing project
            project_id = deployment.railway_project_id
            service_id = deployment.railway_service_id
            
            # Update the service with new Docker image
            update_service_mutation = """
            mutation UpdateService($id: String!, $input: ServiceUpdateInput!) {
                serviceUpdate(id: $id, input: $input) {
                    id
                    name
                }
            }
            """
            
            update_variables = {
                "id": service_id,
                "input": {
                    "source": {
                        "image": deployment.docker_image
                    }
                }
            }
            
            try:
                client._make_request(update_service_mutation, update_variables)
                action = "Redeployed"
                # Save to update timestamp
                deployment.save()
            except Exception as e:
                # If update fails, try creating a new service in the same project
                service = client.deploy_docker_image(
                    project_id=project_id,
                    docker_image=deployment.docker_image,
                    service_name=None
                )
                service_id = service["id"]
                deployment.railway_service_id = service_id
                deployment.save()
                action = "New service created"
        else:
            # First time deployment - create new project
            project = client.create_project(deployment.project_name)
            project_id = project["id"]
            
            # Deploy Docker container
            service = client.deploy_docker_image(
                project_id=project_id,
                docker_image=deployment.docker_image,
                service_name=None
            )
            service_id = service["id"]
            
            # Save project and service IDs
            deployment.railway_project_id = project_id
            deployment.railway_service_id = service_id
            deployment.save()
            
            action = "Deployed"
        
        # Set environment variables if provided
        service_env_vars = {}
        if deployment.stream_key:
            service_env_vars["STREAM_KEY"] = deployment.stream_key
        if deployment.youtube_id:
            service_env_vars["YouTube_ID"] = deployment.youtube_id
        
        if service_env_vars:
            client.set_environment_variables(
                service_id=service_id,
                environment_variables=service_env_vars
            )
        
        # Update service_id if it changed
        if deployment.railway_service_id != service_id:
            deployment.railway_service_id = service_id
            deployment.save()
        
        messages.success(
            request,
            f'✅ {action} successfully! Project: {deployment.project_name}<br>'
            f'Project ID: {project_id}<br>'
            f'Service ID: {service_id}<br>'
            f'<a href="https://railway.app/project/{project_id}" target="_blank">View on Railway</a>'
        )
        
    except ValueError as e:
        error_msg = str(e)
        # Extract more user-friendly error messages
        if "GraphQL errors" in error_msg:
            error_msg = error_msg.replace("GraphQL errors: ", "")
        messages.error(request, f'❌ Deployment failed: {error_msg}')
    except Exception as e:
        messages.error(request, f'❌ Deployment failed: {str(e)}')
    
    return redirect('deployments:deployment_detail', pk=pk)

