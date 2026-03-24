import asyncio
import websockets
import json
import requests
from datetime import datetime, timezone

# --- CONFIGURATION ---
API_KEY = "257d535f8f35d805b11cbec507de61212ccd4508"
URL_DJANGO = "http://127.0.0.1:8000/api/detections/"

# ─── Zones géographiques ───────────────────────────────────────────────────────
# Zone élargie : Détroit de Gibraltar + côte marocaine
# Tanger Ville : 35.79°N, 5.81°W  |  Tanger Med : 35.89°N, 5.50°W
ZONE_DETROIT = [[34.0, -8.0], [37.0, -3.0]]

async def connecter_ais_stream():
    while True:
        try:
            print(f"\n🔄 [{datetime.now().strftime('%H:%M:%S')}] Connexion à AISStream.io...")
            print(f"   📍 Zone : Tanger Med (35.89°N, 5.50°W) + Tanger Ville (35.79°N, 5.81°W)")
            print(f"   🔑 API Key : {API_KEY[:12]}...")

            async with websockets.connect(
                "wss://stream.aisstream.io/v0/stream",
                ping_interval=30,
                ping_timeout=10
            ) as websocket:

                subscribe_msg = {
                    "APIKey": API_KEY,
                    "BoundingBoxes": [ZONE_DETROIT],
                }

                await websocket.send(json.dumps(subscribe_msg))
                print("✅ Connecté ! En attente de messages AIS...\n")

                msg_count: int = int(0)
                async for message in websocket:
                    data = json.loads(message)

                    # ─── Vérifier message d'erreur API ───────────────────────
                    if "Error" in data or "error" in data:
                        print(f"🔴 Erreur AISStream : {data}")
                        continue

                    msg_count += 1  # type: ignore[misc]
                    meta     = data.get("MetaData", {})
                    mmsi     = meta.get("MMSI")
                    lat      = meta.get("latitude")
                    lon      = meta.get("longitude")
                    ship_name = meta.get("ShipName", "Inconnu").strip()
                    ship_type = meta.get("ShipType", 0)
                    msg_type  = data.get("MessageType", "")

                    # Afficher les 3 premiers messages bruts pour diagnostic
                    if msg_count <= 3:
                        print(f"📡 Msg #{msg_count} | Type={msg_type} | MMSI={mmsi} | lat={lat} | lon={lon} |船={ship_name}")

                    # ─── Extraction de la vitesse ─────────────────────────────
                    vitesse = 0.0
                    if msg_type == "PositionReport":
                        vitesse = data.get("Message", {}).get("PositionReport", {}).get("Sog", 0.0)
                    elif msg_type == "StandardClassBPositionReport":
                        vitesse = data.get("Message", {}).get("StandardClassBPositionReport", {}).get("Sog", 0.0)
                    elif msg_type == "ExtendedClassBPositionReport":
                        vitesse = data.get("Message", {}).get("ExtendedClassBPositionReport", {}).get("Sog", 0.0)

                    # Vitesse par défaut selon type navire
                    if not vitesse or vitesse <= 0:
                        if ship_type in [60, 70, 80]:
                            vitesse = 12.0
                        elif ship_type == 30:
                            vitesse = 8.0
                        else:
                            vitesse = 6.0

                    if lat and lon and mmsi:
                        # ✅ FORMAT GEOJSON — obligatoire pour GeoFeatureModelSerializer
                        payload = {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [float(lon), float(lat)]
                            },
                            "properties": {
                                "source": "ais",
                                "mmsi": str(mmsi),
                                "ship_type": int(ship_type) if ship_type else 30,
                                "speed": float(vitesse),
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            }
                        }

                        try:
                            res = requests.post(URL_DJANGO, json=payload, timeout=5)
                            if ship_type and ship_type >= 70:
                                icon = "🚢"
                            elif ship_type == 30:
                                icon = "🎣"
                            else:
                                icon = "🛳️"

                            if res.status_code in (200, 201):
                                print(f"{icon} {ship_name[:18]:<18} | MMSI: {mmsi:<12} | {vitesse:>5.1f} kn | ✅ {res.status_code}")
                            else:
                                # 🔍 Log complet pour débugger
                                print(f"⚠️  {ship_name[:18]:<18} | MMSI: {mmsi:<12} | ❌ HTTP {res.status_code}")
                                print(f"    → Réponse Django : {res.text[:400]}")

                        except requests.exceptions.Timeout:
                            print(f"⏱️  Timeout Django pour MMSI {mmsi}")
                        except requests.exceptions.ConnectionError:
                            print(f"🔴 Serveur Django inaccessible — est-il démarré sur le port 8000 ?")
                        except Exception as e:
                            print(f"❌ Erreur envoi Django: {e}")

        except websockets.exceptions.InvalidStatusCode as e:
            print(f"🔴 Authentification AISStream échouée (HTTP {e.status_code})")
            print(f"   → Vérifiez votre API_KEY sur https://aisstream.io/")
            await asyncio.sleep(15)
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"🔌 Connexion WS fermée ({e}). Reconnexion dans 5s...")
            await asyncio.sleep(5)
        except Exception as error:
            print(f"🔌 Erreur inattendue : {error}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(connecter_ais_stream())
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du client AIS.")