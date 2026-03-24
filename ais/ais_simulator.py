# import time
# import random
# import requests
# import math
# from datetime import datetime, timezone

# # --- CONFIGURATION ---
# URL_DJANGO = "http://127.0.0.1:8000/api/detections/"
# UPDATE_INTERVAL = 3  # secondes entre chaque mise à jour

# # Zone approximative du détroit (Tanger Med / Tanger Ville)
# # Lat: 35.75 à 35.95
# # Lon: -5.90 à -5.40

# class MockVessel:
#     def __init__(self, mmsi, name, ship_type, start_lat, start_lon, speed, heading):
#         self.mmsi = mmsi
#         self.name = name
#         self.ship_type = ship_type
#         self.lat = start_lat
#         self.lon = start_lon
#         self.speed = speed
#         self.heading = heading  # degrés (0 = Nord, 90 = Est, etc.)

#     def move(self, seconds):
#         # Conversion vitesse (noeuds) en degrés environ (très simplifié)
#         # 1 noeud = 1 mille marin / heure ≈ 1/60 degré / heure
#         # Distance en degrés par seconde :
#         speed_deg_per_sec = (self.speed / 3600.0) / 60.0
        
#         distance = speed_deg_per_sec * seconds
        
#         # Variations aléatoires du cap et de la vitesse
#         self.heading += random.uniform(-5, 5)
#         self.speed += random.uniform(-0.5, 0.5)
#         self.speed = max(0, min(self.speed, 30)) # Garder entre 0 et 30 noeuds
        
#         rad_heading = math.radians(self.heading)
        
#         # Déplacement
#         self.lat += distance * math.cos(rad_heading)
#         self.lon += distance * math.sin(rad_heading)
        
#         # Rebondir si on sort trop de la zone de Tanger (très basique)
#         if self.lat > 36.0 or self.lat < 35.7:
#             self.heading = (180 - self.heading) % 360
#         if self.lon > -5.2 or self.lon < -6.0:
#             self.heading = (360 - self.heading) % 360

# # --- INITIALISATION DES NAVIRES ---
# vessels = [
#     MockVessel("244000000", "FERRY TANGER 1", 60, 35.79, -5.81, 18.0, 45),
#     MockVessel("244000001", "CARGO MAROC", 70, 35.89, -5.50, 12.0, 270),
#     MockVessel("244000002", "FISHING BOAT 1", 30, 35.85, -5.70, 5.0, 180),
#     MockVessel("244000003", "TANKER GIB 1", 80, 35.90, -5.60, 10.0, 90),
#     MockVessel("244000004", "YACHT LUX 1", 37, 35.80, -5.75, 20.0, 315),
#     MockVessel("244000005", "FERRY ALGECIRAS", 60, 35.95, -5.45, 19.5, 225),
#     MockVessel("244000006", "CONTAINER ONE", 70, 35.92, -5.55, 14.0, 260),
#     MockVessel("244000007", "FISHING BOAT 2", 30, 35.82, -5.85, 4.5, 10),
#     MockVessel("244000008", "TANKER GIB 2", 80, 35.88, -5.65, 11.2, 85),
#     MockVessel("244000009", "YACHT LUX 2", 37, 35.78, -5.80, 22.0, 15),
#     MockVessel("244000010", "FAST SPIRIT", 40, 35.85, -5.60, 35.0, 300),  # Modifié: Type 40 (Haute vitesse)
#     MockVessel("244000011", "BULK CARRIER A", 70, 35.91, -5.52, 10.5, 250),
#     MockVessel("244000012", "PATROL BOAT", 90, 35.83, -5.78, 28.0, 60),     # Type 90 (Autre)
#     MockVessel("244000013", "LNG TANKER", 80, 35.87, -5.58, 13.0, 110),
#     MockVessel("244000014", "SAILING YACHT", 36, 35.77, -5.83, 6.0, 330),
# ]

# def get_vessel_icon(ship_type):
#     if 30 <= ship_type < 40: return "🎣" # Pêche (30)
#     if 40 <= ship_type < 50: return "🚤" # Haute vitesse (40)
#     if 60 <= ship_type < 70: return "⛴️" # Passager (60)
#     if 70 <= ship_type < 80: return "🚢" # Cargo (70)
#     if 80 <= ship_type < 90: return "🛢️" # Tanker (80)
#     return "🛳️" # Autre

# def run_simulator():
#     print(f"🚀 Démarrage du simulateur AIS ({len(vessels)} navires)")
#     print(f"📡 Envoi des données vers : {URL_DJANGO}")
#     print("Appuyez sur Ctrl+C pour arrêter.\n")
    
#     try:
#         while True:
#             for vessel in vessels:
#                 vessel.move(UPDATE_INTERVAL)
                
#                 payload = {
#                     "type": "Feature",
#                     "geometry": {
#                         "type": "Point",
#                         "coordinates": [round(vessel.lon, 6), round(vessel.lat, 6)]
#                     },
#                     "properties": {
#                         "source": "ais",
#                         "mmsi": str(vessel.mmsi),
#                         "ship_type": vessel.ship_type,
#                         "speed": round(vessel.speed, 1),
#                         "timestamp": datetime.now(timezone.utc).isoformat()
#                     }
#                 }
                
#                 try:
#                     res = requests.post(URL_DJANGO, json=payload, timeout=2)
                    
#                     # Choix de l'icône basé sur la classification standard (mise à jour)
#                     icon = get_vessel_icon(vessel.ship_type)
                        
#                     status = "✅" if res.status_code in (200, 201) else f"❌ HTTP {res.status_code}: {res.text[:150]}"
#                     print(f"{icon} {vessel.name[:15]:<15} | MMSI: {vessel.mmsi} | Cap: {int(vessel.heading):03d}° | {vessel.speed:>4.1f} kn | {status}")
                
#                 except requests.exceptions.ConnectionError:
#                     print(f"🔴 Serveur Django inaccessible à {URL_DJANGO}")
#                 except Exception as e:
#                     print(f"⚠️ Erreur: {e}")
                    
#             print("-" * 50)
#             time.sleep(UPDATE_INTERVAL)
            
#     except KeyboardInterrupt:
#         print("\n🛑 Arrêt du simulateur.")

# if __name__ == "__main__":
#     run_simulator()
import time
import random
import requests
import math
from datetime import datetime, timezone

# --- CONFIGURATION ---
URL_DJANGO = "http://127.0.0.1:8000/api/detections/"
UPDATE_INTERVAL = 3  # secondes

# Zone du détroit
LAT_MIN, LAT_MAX = 35.75, 35.95
LON_MIN, LON_MAX = -5.90, -5.40


# --- FILTRE MER (évite la terre) ---
def get_maroc_coast_lat(lon):
    """Calcule la latitude approximative de la côte marocaine pour une longitude donnée."""
    if lon < -5.81:
        # De Cap Spartel vers Tanger Ville
        return 35.79 + (lon - -5.92) * ((35.78 - 35.79) / (-5.81 - -5.92))
    elif lon < -5.50:
        # Baie de Tanger jusqu'à Tanger Med
        return 35.78 + (lon - -5.81) * ((35.89 - 35.78) / (-5.50 - -5.81))
    else:
        # De Tanger Med vers Ceuta
        return 35.89 + (lon - -5.50) * ((35.88 - 35.89) / (-5.40 - -5.50))

def is_in_sea(lat, lon):
    # L'Espagne (Tarifa) est au nord de 36.00, donc tout ce qui est < 35.95 est soit la mer soit le Maroc
    if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
        return False
        
    # On ajoute un petit buffer de 0.005 degrés (~500m) pour éviter que les bateaux touchent vraiment la côte
    coast_lat = get_maroc_coast_lat(lon) + 0.005
    
    if lat < coast_lat:
        return False # Dans les terres au Maroc !
        
    return True


def random_sea_position():
    while True:
        lat = random.uniform(LAT_MIN, LAT_MAX)
        lon = random.uniform(LON_MIN, LON_MAX)
        if is_in_sea(lat, lon):
            return lat, lon


# --- CLASSE NAVIRE ---
class MockVessel:
    def __init__(self, mmsi, name, ship_type, start_lat, start_lon, speed, heading):
        self.mmsi = mmsi
        self.name = name
        self.ship_type = ship_type
        self.lat = start_lat
        self.lon = start_lon
        self.speed = speed
        self.heading = heading

    def move(self, seconds):
        speed_deg_per_sec = (self.speed / 3600.0) / 60.0
        distance = speed_deg_per_sec * seconds

        # Mouvement plus réaliste
        self.heading += random.uniform(-2, 2)
        self.speed += random.uniform(-0.3, 0.3)
        self.speed = max(0, min(self.speed, 25))

        rad_heading = math.radians(self.heading)

        new_lat = self.lat + distance * math.cos(rad_heading)
        new_lon = self.lon + distance * math.sin(rad_heading)

        # Vérifier si en mer
        if is_in_sea(new_lat, new_lon):
            self.lat = new_lat
            self.lon = new_lon
        else:
            # rebond si touche terre
            self.heading = (self.heading + 180) % 360

        # parfois arrêt (port ou pêche)
        if random.random() < 0.02:
            self.speed = 0


# --- GÉNÉRATION NAVIRES ---
SHIP_TYPES = [30, 37, 40, 60, 70, 80, 90]

def generate_vessels(n=50):
    vessels = []
    for i in range(n):
        lat, lon = random_sea_position()

        vessels.append(MockVessel(
            mmsi=str(244000000 + i),
            name=f"VESSEL {i}",
            ship_type=random.choice(SHIP_TYPES),
            start_lat=lat,
            start_lon=lon,
            speed=random.uniform(2, 20),
            heading=random.uniform(0, 360)
        ))
    return vessels


vessels = generate_vessels(50)  # 🔥 nombre de bateaux ici


# --- ICONES ---
def get_vessel_icon(ship_type):
    if 30 <= ship_type < 40: return "🎣"
    if 40 <= ship_type < 50: return "🚤"
    if 60 <= ship_type < 70: return "⛴️"
    if 70 <= ship_type < 80: return "🚢"
    if 80 <= ship_type < 90: return "🛢️"
    return "🛳️"


# --- SIMULATEUR ---
def run_simulator():
    print(f"🚀 AIS Simulator ({len(vessels)} navires)")
    print(f"📡 URL: {URL_DJANGO}\n")

    try:
        while True:
            for vessel in vessels:
                vessel.move(UPDATE_INTERVAL)

                payload = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            round(vessel.lon, 6),
                            round(vessel.lat, 6)
                        ]
                    },
                    "properties": {
                        "source": "ais",
                        "mmsi": vessel.mmsi,
                        "ship_type": vessel.ship_type,
                        "speed": round(vessel.speed, 1),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }

                try:
                    res = requests.post(URL_DJANGO, json=payload, timeout=2)
                    icon = get_vessel_icon(vessel.ship_type)

                    status = "✅" if res.status_code in (200, 201) else f"❌ {res.status_code}"

                    print(f"{icon} {vessel.name:<12} | {vessel.speed:>4.1f} kn | Cap {int(vessel.heading):03d}° | {status}")

                except requests.exceptions.ConnectionError:
                    print("🔴 Django non accessible")
                except Exception as e:
                    print(f"⚠️ {e}")

            print("-" * 50)
            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        print("\n🛑 Arrêt du simulateur")


# --- MAIN ---
if __name__ == "__main__":
    run_simulator()