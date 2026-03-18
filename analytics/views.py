from rest_framework.views import APIView
from rest_framework.response import Response
from .services import compute_congestion
from bateaux.models import Boat
from .eta_service import predict_eta_for_boat
from rest_framework import status


class PortAnalyticsView(APIView):

    def get(self, request, port_id):

        level, boats_count = compute_congestion(port_id)

        return Response({"port_id": port_id,"boats_in_port": boats_count,"congestion_level": level})
    
class BoatETAView(APIView):
    def get(self, request, mmsi):
        try:
            # 1. Récupérer le bateau
            boat = Boat.objects.get(mmsi=mmsi)
            
            # 2. Récupérer la dernière détection pour avoir lat/lon et vitesse
            derniere_detection = boat.positions.order_by('-timestamp').first()
            
            if not derniere_detection:
                return Response({"error": "Aucune position trouvée"}, status=404)

            # Coordonnées Géo (PointField: x=lon, y=lat)
            current_lon = derniere_detection.location.x
            current_lat = derniere_detection.location.y
            current_speed = derniere_detection.speed # Récupérée de l'AISStream

            # 3. Calculer l'ETA via le service v2 (XGBoost)
            eta_minutes, port_id = predict_eta_for_boat(
                boat, 
                current_lat, 
                current_lon, 
                current_speed
            )

            port_nom = "Tanger Ville" if port_id == 0 else "Tanger Med"

            # 4. Retourner la réponse complète
            return Response({
                "mmsi": mmsi,
                "nom": boat.name or "Inconnu",
                "type": boat.ship_type,
                "vitesse_actuelle": current_speed,
                "port_destination": port_nom,
                "eta_predite_minutes": round(eta_minutes, 2),
                "timestamp_actuel": derniere_detection.timestamp
            })

        except Boat.DoesNotExist:
            return Response({"error": "Bateau non trouvé"}, status=404)