from django import forms
from .models import RailwayDeployment


class RailwayDeploymentForm(forms.ModelForm):
    """Form for Railway deployment configuration."""
    
    class Meta:
        model = RailwayDeployment
        fields = [
            'railway_token',
            'project_name',
            'docker_image',
            'stream_key',
            'youtube_id',
        ]
        widgets = {
            'railway_token': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Railway API token',
                'type': 'password',  # Hide token input
            }),
            'project_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Live Stream',
            }),
            'docker_image': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'imvickykumar999/stream-downloader',
            }),
            'stream_key': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your YouTube stream key (optional)',
            }),
            'youtube_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '4UTdZpN26Bs (optional)',
            }),
        }
        help_texts = {
            'railway_token': 'Get it from <a href="https://railway.com/account/tokens" target="_blank">Railway Account Tokens</a>',
            'project_name': 'Use a unique name for your project',
            'docker_image': 'Docker image to deploy (e.g., imvickykumar999/stream-downloader)',
            'stream_key': 'Get it from <a href="https://studio.youtube.com/channel/UC/livestreaming" target="_blank">YouTube Studio Livestreaming</a>',
            'youtube_id': 'YouTube video ID (e.g., 4UTdZpN26Bs from https://www.youtube.com/watch?v=4UTdZpN26Bs)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make required fields more obvious
        self.fields['railway_token'].required = True
        self.fields['project_name'].required = True
        self.fields['docker_image'].required = True

