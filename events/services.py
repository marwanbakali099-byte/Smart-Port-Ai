from ports.models import Port
from .models import PortEvent
from ports.utils import get_port_from_position

def check_entry_exit(boat, new_detection):
    # On récupère le port où se trouve le bateau MAINTENANT
    current_port = get_port_from_position(new_detection.location.y, new_detection.location.x)
    
    # On récupère sa position PRÉCÉDENTE
    last_detection = boat.positions.exclude(id=new_detection.id).order_by('-timestamp').first()
    if not last_detection: return
    
    # On regarde si avant il était dans un port
    previous_port = get_port_from_position(last_detection.location.y, last_detection.location.x)

    # LOGIQUE D'ENTRÉE
    if not previous_port and current_port:
        PortEvent.objects.create(boat=boat, port=current_port, event_type="entry", timestamp=new_detection.timestamp)
        print(f"✅ {boat.mmsi} est entré à {current_port.name}")

    # LOGIQUE DE SORTIE
    elif previous_port and not current_port:
        PortEvent.objects.create(boat=boat, port=previous_port, event_type="exit", timestamp=new_detection.timestamp)
        print(f"🚪 {boat.mmsi} a quitté {previous_port.name}")