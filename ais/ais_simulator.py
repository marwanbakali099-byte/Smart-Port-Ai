import requests
import time
from datetime import datetime
import random

URL_DJANGO = "http://127.0.0.1:8000/api/detections/"

BATEAUX = [
    {"mmsi": "242012345", "name": "MAROC_EXPRESS"},
    {"mmsi": "242055667", "name": "TANGER_FERRY"},
    {"mmsi": "311000999", "name": "CARGO_ONE"},
]

def simuler_mouvement():
    toggle = True
    while True:
        for bateau in BATEAUX:
            if toggle:
                lat, lon = 35.88, -5.80  # inside
            else:
                lat, lon = 35.80, -5.85  # outside

            payload = {
                "source": "ais",
                "mmsi": bateau["mmsi"],
                "location": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.95
            }

            try:
                r = requests.post(URL_DJANGO, json=payload)
                print(f"{bateau['name']} -> {r.status_code}")
            except Exception as e:
                print("❌ Error:", e)

        toggle = not toggle
        time.sleep(5)

if __name__ == "__main__":
    simuler_mouvement()