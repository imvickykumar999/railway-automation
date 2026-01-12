import os
import sys
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.safestring import mark_safe
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


@login_required
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


@login_required
def deployment_list(request):
    """Display list of all deployment configurations."""
    deployments = RailwayDeployment.objects.all()
    return render(request, 'deployments/list.html', {'deployments': deployments})


@login_required
def deployment_detail(request, pk):
    """Display details of a specific deployment configuration."""
    try:
        deployment = RailwayDeployment.objects.get(pk=pk)
    except RailwayDeployment.DoesNotExist:
        messages.error(request, 'Deployment configuration not found.')
        return redirect('deployments:deployment_list')
    
    return render(request, 'deployments/detail.html', {'deployment': deployment})


@login_required
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


@login_required
def deployment_delete(request, pk):
    """Delete a deployment configuration and Railway project."""
    try:
        deployment = RailwayDeployment.objects.get(pk=pk)
        if request.method == 'POST':
            # Delete Railway project if it exists
            if deployment.railway_project_id and RailwayClient is not None:
                try:
                    client = RailwayClient(deployment.railway_token)
                    
                    # Delete Railway project
                    delete_project_mutation = """
                    mutation DeleteProject($id: String!) {
                        projectDelete(id: $id)
                    }
                    """
                    
                    try:
                        client._make_request(delete_project_mutation, {"id": deployment.railway_project_id})
                        messages.success(
                            request,
                            f'Railway project "{deployment.project_name}" deleted successfully! '
                            f'Local configuration also deleted.'
                        )
                    except Exception as e:
                        # If Railway deletion fails, still delete local record
                        error_msg = str(e)
                        if "GraphQL errors" in error_msg:
                            error_msg = error_msg.replace("GraphQL errors: ", "")
                        messages.warning(
                            request,
                            f'Could not delete Railway project: {error_msg}. '
                            f'Local configuration deleted anyway.'
                        )
                except Exception as e:
                    messages.warning(
                        request,
                        f'Error connecting to Railway API: {str(e)}. '
                        f'Local configuration deleted anyway.'
                    )
            
            # Delete local database record
            project_name = deployment.project_name
            had_railway_project = bool(deployment.railway_project_id)
            deployment.delete()
            
            # If no Railway project was deleted, show simple success message
            if not had_railway_project:
                messages.success(request, f'Deployment configuration "{project_name}" deleted successfully!')
            
            return redirect('deployments:deployment_list')
    except RailwayDeployment.DoesNotExist:
        messages.error(request, 'Deployment configuration not found.')
        return redirect('deployments:deployment_list')
    
    return render(request, 'deployments/delete.html', {'deployment': deployment})


@login_required
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
            # Redeploy to existing project - delete old service and create new one
            project_id = deployment.railway_project_id
            old_service_id = deployment.railway_service_id
            
            # Delete the existing service
            delete_service_mutation = """
            mutation DeleteService($id: String!) {
                serviceDelete(id: $id)
            }
            """
            
            try:
                client._make_request(delete_service_mutation, {"id": old_service_id})
            except Exception as e:
                # If deletion fails, log but continue (service might already be deleted)
                pass
            
            # Create a new service in the same project
            service = client.deploy_docker_image(
                project_id=project_id,
                docker_image=deployment.docker_image,
                service_name=None
            )
            service_id = service["id"]
            
            # Update service_id in database
            deployment.railway_service_id = service_id
            deployment.save()
            
            action = "Redeployed"
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
            mark_safe(
                f'✅ <strong>{action} successfully!</strong><br>'
                f'<strong>Project:</strong> {deployment.project_name}<br>'
                f'<strong>Project ID:</strong> {project_id}<br>'
                f'<strong>Service ID:</strong> {service_id}<br>'
                f'<a href="https://railway.app/project/{project_id}" target="_blank" style="color: #90ee90; text-decoration: underline; font-weight: 600;">View on Railway →</a>'
            )
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

