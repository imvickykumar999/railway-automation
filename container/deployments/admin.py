from django.contrib import admin
from .models import RailwayDeployment


@admin.register(RailwayDeployment)
class RailwayDeploymentAdmin(admin.ModelAdmin):
    list_display = ['project_name', 'docker_image', 'railway_project_id', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['project_name', 'docker_image', 'railway_project_id']
    readonly_fields = ['created_at', 'updated_at', 'railway_project_id', 'railway_service_id']
    
    fieldsets = (
        ('Required Configuration', {
            'fields': ('railway_token', 'project_name', 'docker_image')
        }),
        ('YouTube Configuration', {
            'fields': ('stream_key', 'youtube_id'),
            'classes': ('collapse',)
        }),
        ('Railway Deployment Info', {
            'fields': ('railway_project_id', 'railway_service_id'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

