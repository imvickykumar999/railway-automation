from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class RailwayDeployment(models.Model):
    """Model to store Railway deployment configuration."""
    
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
    
    # Optional fields
    stream_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Get it from https://studio.youtube.com/channel/UC/livestreaming",
        verbose_name="Stream Key"
    )
    
    youtube_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="YouTube video ID (e.g., 4UTdZpN26Bs from https://www.youtube.com/watch?v=4UTdZpN26Bs)",
        verbose_name="YouTube ID"
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

