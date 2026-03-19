from rest_framework.views import APIView
from rest_framework.response import Response
from .port_service import get_avg_eta, get_boats_in_port, get_congestion
from .services import calculate_real_fishing_hours, compute_congestion
from bateaux.models import Boat
from .eta_service import predict_eta_for_boat
from django.shortcuts import get_object_or_404
from ports.models import Port
from .congestion_model import predictor
from datetime import datetime

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
        
class PortStatusView(APIView):
    def get(self, request, port_id):
        boats = get_boats_in_port(port_id)
        count = len(boats)
        avg_eta = get_avg_eta(boats)

        return Response({
            "port_id": port_id,
            "boats_in_port": count,
            "boats": [b.mmsi for b in boats],
            "avg_eta_minutes": avg_eta,
            "congestion": get_congestion(count)
        })

class PortCongestionIAView(APIView):
    def get(self, request, port_id):
        # 1. Récupérer le port (Ne pas oublier cette ligne !)
        port = get_object_or_404(Port, id=port_id)

        # 2. Préparer les données réelles
        metrics = calculate_real_fishing_hours(port) 

        # Extraction sécurisée
        mmsi_present = metrics.get('boats_count', 0)
        real_fishing_hours = metrics.get('fishing_hours', 0.0)
        current_hour = metrics.get('hour', datetime.now().hour)

        # 3. Lancer la prédiction IA
        # Note: Assure-toi que ton predictor.predict renvoie bien (label, score)
        prediction_label, raw_score = predictor.predict(
            hours=current_hour, 
            fishing_hours=real_fishing_hours, 
            mmsi_present=mmsi_present
        )

        # 4. Réponse enrichie pour le Front-end
        return Response({
            "port_name": port.name,
            "congestion_predictive_ia": prediction_label,
            "confidence_score": round(raw_score, 4),
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": metrics 
        })