"""
URL configuration for railway_config project.
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.i18n import set_language
from django.views.generic import CreateView
from django.conf import settings
from django.conf.urls.static import static
from deployments.forms import CustomUserCreationForm, CustomAuthenticationForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', CreateView.as_view(
        template_name='registration/register.html',
        form_class=CustomUserCreationForm,
        success_url='../login/'
    ), name='register'),
    path('', include('deployments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
