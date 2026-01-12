from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class RailwayDeployment(models.Model):
    """Model to store Railway deployment configuration."""
    
    # User who owns this deployment
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='deployments',
        verbose_name='Owner',
        null=True,
        blank=True
    )
    
    # Required fields
    railway_token = models.CharField(
        max_length=255,
        help_text="Get it from https://railway.com/account/tokens",
        verbose_name="Railway Token"
    )
    
    project_name = models.CharField(
        max_length=255,
        default="Live Stream",
        help_text="Use a unique name for your project",
        verbose_name="Project Name"
    )
    
    docker_image = models.CharField(
        max_length=255,
        default="imvickykumar999/stream-downloader",
        help_text="Docker image to deploy (e.g., imvickykumar999/stream-downloader)",
        verbose_name="Docker Image"
    )
    
    # Required fields
    stream_key = models.CharField(
        max_length=255,
        default='',
        help_text="Get it from https://studio.youtube.com/channel/UC/livestreaming",
        verbose_name="Stream Key"
    )
    
    youtube_id = models.CharField(
        max_length=50,
        default='',
        help_text="YouTube video ID (e.g., 4UTdZpN26Bs from https://www.youtube.com/watch?v=4UTdZpN26Bs)",
        verbose_name="YouTube ID"
    )
    
    # Deployment tracking
    railway_project_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Railway project ID (set after first deployment)",
        verbose_name="Railway Project ID"
    )
    
    railway_service_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Railway service ID (set after first deployment)",
        verbose_name="Railway Service ID"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Active configuration")
    
    class Meta:
        verbose_name = "Railway Deployment"
        verbose_name_plural = "Railway Deployments"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project_name} - {self.docker_image}"
    
    def clean(self):
        """Validate the model data."""
        super().clean()
        
        # Validate YouTube ID format if provided
        if self.youtube_id:
            # YouTube IDs are typically 11 characters
            if len(self.youtube_id) != 11:
                raise ValidationError({
                    'youtube_id': 'YouTube ID should be 11 characters long.'
                })
    
    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()
        super().save(*args, **kwargs)

