from django import forms
from .models import RailwayDeployment


class RailwayDeploymentForm(forms.ModelForm):
    """Form for Railway deployment configuration."""
    
    # Docker image choices
    DOCKER_IMAGE_CHOICES = [
        ('imvickykumar999/youtube-stream', 'Long lasting stream'),
        ('imvickykumar999/stream-downloader', 'High quality stream'),
    ]
    
    # Override docker_image field to use dropdown
    docker_image = forms.ChoiceField(
        choices=DOCKER_IMAGE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        help_text='Select a Docker image to deploy',
        required=True
    )
    
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
            'stream_key': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your YouTube stream key',
                'type': 'password',  # Hide stream key input
            }),
            'youtube_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'YouTube Video ID',
            }),
        }
        help_texts = {
            'railway_token': 'Get it from <a href="https://railway.com/account/tokens" target="_blank">Railway Account Tokens</a>',
            'project_name': 'Use a unique name for your project',
            'stream_key': 'Get it from <a href="https://studio.youtube.com/channel/UC/livestreaming" target="_blank">YouTube Studio Livestreaming</a>',
            'youtube_id': 'YouTube video ID (e.g., 4UTdZpN26Bs from https://www.youtube.com/watch?v=4UTdZpN26Bs)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required
        self.fields['railway_token'].required = True
        self.fields['project_name'].required = True
        self.fields['docker_image'].required = True
        self.fields['stream_key'].required = True
        self.fields['youtube_id'].required = True
        
        # Set default value for docker_image if instance exists
        if self.instance and self.instance.pk:
            current_value = self.instance.docker_image
            if current_value:
                # If current value is not in choices, add it as an option
                if current_value not in [choice[0] for choice in self.DOCKER_IMAGE_CHOICES]:
                    self.fields['docker_image'].choices = [
                        (current_value, f'{current_value} (current)'),
                    ] + list(self.DOCKER_IMAGE_CHOICES)
                # Set the initial value to the current value
                self.fields['docker_image'].initial = current_value

