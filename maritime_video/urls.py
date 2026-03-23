from django.urls import path
from .views import LivePortStreamView, BoatStatsView

urlpatterns = [
    # URL pour voir la vidéo (le flux d'images)
    # Accessible via : /api/video/stream/
    path('stream/', LivePortStreamView.as_view(), name='video_stream'),

    # URL pour récupérer les données JSON (pour les graphiques du front)
    # Accessible via : /api/video/stats/
    path('stats/', BoatStatsView.as_view(), name='video_stats'),
]