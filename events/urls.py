from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PortEventViewSet

router = DefaultRouter()
router.register(r'events', PortEventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
]
