from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView # Import this

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Add this specific path to fix the 404 error
    path('accounts/profile/', RedirectView.as_view(url='/dashboard/')), 
]