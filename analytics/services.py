from bateaux.models import Boat
from ports.models import Port

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