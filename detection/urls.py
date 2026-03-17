from rest_framework.routers import DefaultRouter
from .views import DetectionViewSet
from django.urls import path,include

router = DefaultRouter()
router.register(r'detections', DetectionViewSet, basename='detection')

# Ici, on définit les urlpatterns propres à l'application
urlpatterns = [
    path('', include(router.urls)),
]