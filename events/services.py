from ports.models import Port
from .models import PortEvent
from django.utils import timezone

def check_entry_exit(detection):
    """
    Analyse si une détection constitue une entrée ou une sortie.
    Correction : On utilise 'boat' au lieu de 'mmsi' pour le filtrage PortEvent.
    """
    boat = detection.boat # On récupère l'objet Boat lié à la détection
    point = detection.location
    
    if not boat:
        print("⚠️ Détection sans bateau associé. Abandon.")
        return

    for port in Port.objects.all():
        is_inside = port.boundary.contains(point)
        
        # Correction ici : on filtre par 'boat' et non 'mmsi'
        last_event = PortEvent.objects.filter(
            port=port, 
            boat=boat
        ).order_by('-timestamp').first()

        # CAS 1 : ENTRÉE
        if is_inside and (not last_event or last_event.event_type == 'exit'):
            PortEvent.objects.create(
                port=port,
                boat=boat, # Utilisation du champ correct
                event_type='entry',
                timestamp=detection.timestamp,
                processed=False
            )
            print(f"📥 ENTRÉE : {boat.mmsi} dans {port.name}")

        # CAS 2 : SORTIE
        elif not is_inside and last_event and last_event.event_type == 'entry':
            # Clôture de l'entrée
            PortEvent.objects.filter(
                port=port, 
                boat=boat, 
                event_type='entry', 
                processed=False
            ).update(processed=True)
            
            # Création de la sortie
            PortEvent.objects.create(
                port=port,
                boat=boat,
                event_type='exit',
                timestamp=detection.timestamp,
                processed=True
            )
            print(f"📤 SORTIE : {boat.mmsi} quitte {port.name}")