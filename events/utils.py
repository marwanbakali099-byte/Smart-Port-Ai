from events.models import PortEvent
from ports.models import Port
from ports.utils import get_port_from_position
from django.utils.timezone import now


def handle_port_event(boat, lat, lon):
    port = get_port_from_position(lat, lon)

    last_event = PortEvent.objects.filter(boat=boat).order_by('-timestamp').first()

    if port:
        if not last_event or last_event.event_type == "exit":
            PortEvent.objects.create(
                boat=boat,
                port=port,
                event_type="entry",
                timestamp=now()
            )
            print(f"🟢 ENTRY → {port.name}")

    else:
        if last_event and last_event.event_type == "entry":
            PortEvent.objects.create(
                boat=boat,
                port=last_event.port,
                event_type="exit",
                timestamp=now()
            )
            print(f"🔴 EXIT → {last_event.port.name}")