from ports.models import Port
from .models import PortEvent

def check_entry_exit(boat, new_detection):

    port = Port.objects.first()
    if not port:
        return

    last_detection = boat.detection_set.exclude(
        id=new_detection.id
    ).order_by('-timestamp').first()

    if not last_detection:
        return

    was_inside_before = port.boundary.contains(last_detection.location)
    is_inside_now = port.boundary.contains(new_detection.location)

    last_event = PortEvent.objects.filter(boat=boat).order_by('-timestamp').first()

    # ENTRY
    if not was_inside_before and is_inside_now:

        if last_event and last_event.event_type == "entry":
            return

        PortEvent.objects.create(
            boat=boat,
            port=port,
            event_type="entry",
            timestamp=new_detection.timestamp
        )

        print(f"{boat.mmsi} ✅ ENTRY detected")

    # EXIT
    elif was_inside_before and not is_inside_now:

        if last_event and last_event.event_type == "exit":
            return

        PortEvent.objects.create(
            boat=boat,
            port=port,
            event_type="exit",
            timestamp=new_detection.timestamp
        )

        print(f"{boat.mmsi} 🚪 EXIT detected")