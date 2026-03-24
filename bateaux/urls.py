from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BoatViewSet

router = DefaultRouter()
router.register(r'bateaux', BoatViewSet, basename='boat')

urlpatterns = [
    path('', include(router.urls)),
]
