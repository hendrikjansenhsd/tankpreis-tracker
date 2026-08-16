"""
Einmalig ausführen: sucht alle Tankstellen im Radius um Oberhausen, Essen
und Duesseldorf und speichert die (deduplizierte) Liste in stations.csv.

Aufruf: python get_stations.py
Benötigt Umgebungsvariable TANKERKOENIG_API_KEY.
"""
import csv
import os
import time

import requests

from config import CITIES, STATIONS_FILE

API_KEY = os.environ["TANKERKOENIG_API_KEY"]
LIST_URL = "https://creativecommons.tankerkoenig.de/json/list.php"


def fetch_stations_for_city(lat, lng, radius_km):
    params = {
        "lat": lat,
        "lng": lng,
        "rad": radius_km,
        "sort": "dist",
        "type": "all",
        "apikey": API_KEY,
    }
    resp = requests.get(LIST_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"API-Fehler: {data}")
    return data["stations"]


def main():
    all_stations = {}
    for city, (lat, lng, radius) in CITIES.items():
        stations = fetch_stations_for_city(lat, lng, radius)
        print(f"{city}: {len(stations)} Tankstellen gefunden")
        for s in stations:
            all_stations[s["id"]] = {
                "id": s["id"],
                "name": s["name"],
                "brand": s["brand"],
                "street": s["street"],
                "place": s["place"],
                "lat": s["lat"],
                "lng": s["lng"],
                "city_search": city,
            }
        time.sleep(65)  # Rate-Limit: max. 1 Request/Minute pro API-Key

    with open(STATIONS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "name", "brand", "street", "place", "lat", "lng", "city_search"],
        )
        writer.writeheader()
        writer.writerows(all_stations.values())

    print(f"\nInsgesamt {len(all_stations)} einzigartige Tankstellen -> {STATIONS_FILE}")


if __name__ == "__main__":
    main()
