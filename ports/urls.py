from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PortViewSet

router = DefaultRouter()
router.register(r'ports', PortViewSet, basename='port')

urlpatterns = [
    path('', include(router.urls)),
]
