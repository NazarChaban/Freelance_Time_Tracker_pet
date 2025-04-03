from django.urls import path, include

app_name = "clients"

urlpatterns = [
    path('api/', include(('clients.api.urls', 'api'), namespace='api')),
]
