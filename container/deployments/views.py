from django.shortcuts import render, redirect
from django.contrib import messages
from .models import RailwayDeployment
from .forms import RailwayDeploymentForm


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

