from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Detection
from .serializers import DetectionSerializer
# Assure-toi que ce service contient la logique de comparaison géospatiale
from events.services import check_entry_exit


class DetectionViewSet(viewsets.ModelViewSet):
    queryset = Detection.objects.all().order_by("-timestamp")
    serializer_class = DetectionSerializer

    def perform_create(self, serializer):
        # 1. On enregistre d'abord la détection en base de données
        detection = serializer.save()

        # 2. On déclenche la logique de vérification Entrée/Sortie
        try:
            check_entry_exit(detection)
            print(f" Check Entry/Exit exécuté pour le MMSI: {detection.mmsi}")
        except Exception as e:
            print(f" Erreur lors du check_entry_exit: {e}")


class AlertListView(APIView):
    """
    GET /api/detections/alerts/
    Retourne les dernières détections formatées comme alertes pour le dashboard.
    """

    def get(self, request):
        # Récupère les 50 dernières détections triées par timestamp desc
        detections = Detection.objects.select_related('boat').order_by('-timestamp')[:50]

        alerts = []
        for det in detections:
            boat_name = None
            if det.boat:
                boat_name = det.boat.name or det.mmsi
            else:
                boat_name = det.mmsi or 'Inconnu'

            alerts.append({
                'id': det.id,
                'mmsi': det.mmsi,
                'vessel_name': boat_name,
                'source': det.source,
                'speed': det.speed,
                'eta_minutes': det.eta_minutes,
                'timestamp': det.timestamp,
                'latitude': det.location.y if det.location else None,
                'longitude': det.location.x if det.location else None,
                'severity': 'high' if det.speed and det.speed > 20 else 'medium' if det.speed and det.speed > 10 else 'low',
                'message': f"Détection {det.source.upper()} — Vitesse: {det.speed:.1f} nœuds",
            })

        return Response(alerts)