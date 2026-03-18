from detection.models import Detection
from django.db.models import Avg
from events.models import PortEvent

# def get_boats_in_port():
#     boats_inside = []

#     events = PortEvent.objects.order_by('boat', '-timestamp').distinct('boat')

#     for event in events:
#         if event.event_type == "entry":
#             boats_inside.append(event.boat)

#     return boats_inside

def get_boats_in_port(port_id=None):
    boats_inside = []
    seen = set()

    # events = PortEvent.objects.order_by('-timestamp')  # important
    if port_id:
        events = PortEvent.objects.filter(port_id=port_id).order_by('-timestamp')
    else:
        events = PortEvent.objects.order_by('-timestamp')

    for event in events:
        if event.boat_id in seen:
            continue

        seen.add(event.boat_id)

        if event.event_type == "entry":
            boats_inside.append(event.boat)

    return boats_inside



def get_avg_eta(boats):
    from detection.models import Detection

    etas = []

    for boat in boats:
        last_detection = Detection.objects.filter(
            mmsi=boat.mmsi,
            eta_minutes__isnull=False
        ).order_by('-timestamp').first()

        if last_detection:
            etas.append(last_detection.eta_minutes)

    if not etas:
        return None

    return sum(etas) / len(etas)

def get_congestion(boats_count):
    capacity = 10  # à ajuster

    ratio = boats_count / capacity

    if ratio < 0.5:
        return "LOW"
    elif ratio < 0.8:
        return "MEDIUM"
    return "HIGH"