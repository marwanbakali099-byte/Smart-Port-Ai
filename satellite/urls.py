from django.urls import path
from .views import SatelliteDetectionView

urlpatterns = [
    # Cet endpoint sera accessible via /api/satellite/detect/
    path('detect/', SatelliteDetectionView.as_view(), name='satellite-detect'),
]