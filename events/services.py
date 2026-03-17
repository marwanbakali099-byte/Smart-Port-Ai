from ports.models import Port
from .models import PortEvent

def check_entry_exit(boat, new_detection):
    port = Port.objects.first()
    if not port or not new_detection.location:
        return

    # Récupère la dernière détection
    last_detection = boat.detection_set.order_by('-timestamp').first()

    # Première détection → considère dehors par défaut
    was_inside_before = False
    if last_detection and last_detection != new_detection:
        was_inside_before = port.boundary.contains(last_detection.location)

    # Est-ce que le bateau est maintenant à l'intérieur ?
    is_inside_now = port.boundary.contains(new_detection.location)

    if not was_inside_before and is_inside_now:
        PortEvent.objects.create(
            boat=boat,
            port=port,
            event_type="entry",
            timestamp=new_detection.timestamp
        )
        print(f"{boat.mmsi} ✅ ENTRY detected")
    elif was_inside_before and not is_inside_now:
        PortEvent.objects.create(
            boat=boat,
            port=port,
            event_type="exit",
            timestamp=new_detection.timestamp
        )
        print(f"{boat.mmsi} 🚪 EXIT detected")