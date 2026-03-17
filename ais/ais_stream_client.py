import asyncio
import websockets
import json
import requests
from datetime import datetime

async def connecter_ais_stream():
    cle_api = "ef62bc9224f99a5da8884ac8a80e315637eaccaa" 
    url_wss = "wss://stream.aisstream.io/v0/stream"
    url_django = "http://127.0.0.1:8000/api/detections/"

    while True: # Boucle pour reconnecter automatiquement
        try:
            async with websockets.connect(url_wss, ping_interval=20) as websocket:
                # Format exact pour AISStream
                subscribe_message = {
                    "APIKey": cle_api,
                    "BoundingBoxes": [[[[34.0, -7.0], [37.0, -4.0]]]] 
                }

                await websocket.send(json.dumps(subscribe_message))
                print("🚀 Abonnement envoyé. Attente des messages...")

                async for message in websocket:
                    try:
                        donnees = json.loads(message)
                        meta = donnees.get("MetaData", {})
                        
                        # AISStream envoie parfois la position dans 'Message' -> 'PositionReport'
                        # ou directement dans 'MetaData'. On vérifie les deux.
                        lat = meta.get("latitude")
                        lon = meta.get("longitude")
                        mmsi = meta.get("MMSI")

                        if lat and lon:
                            payload = {
                                "source": "ais",
                                "mmsi": str(mmsi),
                                "location": {
                                    "type": "Point",
                                    "coordinates": [float(lon), float(lat)]
                                },
                                "timestamp": datetime.utcnow().isoformat()
                            }
                            
                            # Envoi à Django
                            r = requests.post(url_django, json=payload, timeout=2)
                            print(f"🚢 {meta.get('ShipName')} (MMSI: {mmsi}) -> Django: {r.status_code}")

                    except Exception as e:
                        print(f"⚠️ Erreur message: {e}")

        except websockets.exceptions.ConnectionClosedError:
            print("🔌 Serveur déconnecté. Reconnexion dans 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"💥 Erreur critique: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(connecter_ais_stream())