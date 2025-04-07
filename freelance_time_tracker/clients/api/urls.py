from rest_framework.routers import DefaultRouter
from clients.views import ClientViewSet
from django.urls import path, include

app_name = 'api'

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')

urlpatterns = [
    path('', include(router.urls)),
]
