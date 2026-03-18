import asyncio
import websockets
import json
import requests
from datetime import datetime, timezone # Utilisation de timezone pour la compatibilité

# --- CONFIGURATION ---
API_KEY = "257d535f8f35d805b11cbec507de61212ccd4508"
URL_DJANGO = "http://127.0.0.1:8000/api/detections/"

async def connecter_ais_stream():
    zone_tanger = [[34.0, -7.5], [37.0, -4.5]]

    while True:
        try:
            print(f"\n🔄 [{datetime.now().strftime('%H:%M:%S')}] Tentative de connexion à AISStream...")
            
            async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
                
                subscribe_msg = {
                    "APIKey": API_KEY,
                    "BoundingBoxes": [zone_tanger],
                    "FiltersShipType": [30, 60, 70, 80] 
                }

                await websocket.send(json.dumps(subscribe_msg))
                print("✅ Connecté ! Écoute des navires (Pêche, Cargo, Tankers, Ferries)...")

                async for message in websocket:
                    data = json.loads(message)
                    meta = data.get("MetaData", {})
                    mmsi = meta.get("MMSI")
                    lat = meta.get("latitude")
                    lon = meta.get("longitude")
                    ship_name = meta.get("ShipName", "Inconnu").strip()
                    ship_type = meta.get("ShipType", 0)

                    msg_type = data.get("MessageType")
                    vitesse = 0.0
                    
                    if msg_type == "PositionReport":
                        vitesse = data.get("Message", {}).get("PositionReport", {}).get("Sog", 0.0)

                    if lat and lon and mmsi:
                        payload = {
                            "source": "ais",
                            "mmsi": str(mmsi),
                            "ship_type": int(ship_type) if ship_type else 30,
                            "speed": float(vitesse),
                            "location": {
                                "type": "Point",
                                "coordinates": [float(lon), float(lat)]
                            },
                            # Correction de l'erreur UTC ici :
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }

                        try:
                            res = requests.post(URL_DJANGO, json=payload, timeout=2)
                            icon = "🚢" if ship_type and ship_type >= 70 else "🛶"
                            print(f"{icon} {ship_name[:15]:<15} | MMSI: {mmsi} | SOG: {vitesse:>4} kn | Django: {res.status_code}")
                        except Exception as e:
                            print(f"❌ Erreur envoi Django: {e}")

        except Exception as error:
            print(f"🔌 Connexion interrompue ({error}). Reconnexion dans 5s...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(connecter_ais_stream())
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du client AIS.")