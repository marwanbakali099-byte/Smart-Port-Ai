from .congestion_model import predictor
from bateaux.models import Boat
from ports.models import Port

from django.utils import timezone
from datetime import datetime
from django.db.models import F
from events.models import PortEvent 

# fonction pour compter le nombre de bateaux actuellement dans le port
def count_boats_in_port(port_id):

    try:
        port = Port.objects.get(id=port_id)
    except Port.DoesNotExist:
        return 0
    
    boats_in_port = 0

    for boat in Boat.objects.all():

        # last_detection = boat.detection_set.order_by('-timestamp').first()
        last_detection = boat.positions.order_by('-timestamp').first()

        if last_detection and port.boundary.contains(last_detection.location):
            boats_in_port += 1

    return boats_in_port



# calcul du niveau de congestion du port
def compute_congestion(port_id):

    try:
        port = Port.objects.get(id=port_id)
    except Port.DoesNotExist:
        return "UNKNOWN", 0

    boats_count = count_boats_in_port(port_id)
    # pour éviter la division par zéro
    if port.capacity <= 0:
        return "LOW", boats_count

    ratio = boats_count / port.capacity

    if ratio < 0.4:
        level = "LOW"
    elif ratio < 0.7:
        level = "MEDIUM"
    else:
        level = "HIGH"

    return level, boats_count



def get_port_analytics(port):
    # Récupération des données réelles pour l'IA
    boats_count = port.portevent_set.filter(event_type='entry').count() #
    
    # Simulation des heures (à remplacer par vos vrais calculs de temps plus tard)
    current_hour = 12 
    total_fishing_hours = boats_count * 2 

    # Appel à l'IA XGBoost
    congestion_label = predictor.predict(current_hour, total_fishing_hours, boats_count)

    return {
        "port_id": port.id,
        "boats_in_port": boats_count,
        "congestion": congestion_label  # Score venant de l'IA !
    }


def calculate_real_fishing_hours(port):
    now = timezone.now()
    total_seconds = 0
    
    # On récupère les événements d'entrée du port
    # On part du principe que si un bateau est dans 'PortEvent' avec 'entry', 
    # c'est qu'il est lié à un objet 'boat'
    active_entries = PortEvent.objects.filter(port=port, event_type='entry')
    
    count = active_entries.count()
    
    for event in active_entries:
        duration = now - event.timestamp
        total_seconds += max(0, duration.total_seconds())

    fishing_hours = round(total_seconds / 3600, 2)
    current_hour = now.hour
    
    # On récupère les résultats de l'IA
    prediction_label, confidence = predictor.predict(current_hour, fishing_hours, count)
    
    return {
        "port_id": port.id,
        "port_name": port.name,
        "boats_count": count,
        "fishing_hours": fishing_hours,
        "hour": current_hour,
        "congestion": prediction_label,
        "confidence": confidence
    }