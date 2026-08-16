"""
Fragt fuer alle Tankstellen in stations.csv den aktuellen Preis ab und
haengt eine Zeile pro Tankstelle an prices.csv an. Gedacht fuer stuendlichen
Aufruf per GitHub Actions Cronjob.

Aufruf: python collect_prices.py
Benoetigt Umgebungsvariable TANKERKOENIG_API_KEY.
"""
import csv
import os
import time
from datetime import datetime, timezone

import requests

from config import FUEL_TYPE, PRICES_FILE, STATIONS_FILE

API_KEY = os.environ["TANKERKOENIG_API_KEY"]
PRICES_URL = "https://creativecommons.tankerkoenig.de/json/prices.php"
BATCH_SIZE = 10  # API erlaubt max. 10 IDs pro Anfrage
SECONDS_BETWEEN_REQUESTS = 65  # Rate-Limit: max. 1 Request/Minute pro API-Key


def load_station_ids():
    with open(STATIONS_FILE, newline="", encoding="utf-8") as f:
        return [row["id"] for row in csv.DictReader(f)]


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def fetch_prices(ids_batch):
    params = {"ids": ",".join(ids_batch), "apikey": API_KEY}
    resp = requests.get(PRICES_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"API-Fehler: {data}")
    return data["prices"]


def main():
    station_ids = load_station_ids()
    timestamp = datetime.now(timezone.utc).isoformat()

    file_exists = os.path.exists(PRICES_FILE)
    with open(PRICES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp_utc", "station_id", "fuel_type", "price", "status"])

        batches = list(chunks(station_ids, BATCH_SIZE))
        for i, batch in enumerate(batches):
            prices = fetch_prices(batch)
            for station_id, info in prices.items():
                if not info.get("status") == "open":
                    writer.writerow([timestamp, station_id, FUEL_TYPE, "", info.get("status")])
                    continue
                price = info.get(FUEL_TYPE)
                writer.writerow([timestamp, station_id, FUEL_TYPE, price, "open"])
            f.flush()
            if i < len(batches) - 1:
                time.sleep(SECONDS_BETWEEN_REQUESTS)

    print(f"{timestamp}: Preise fuer {len(station_ids)} Tankstellen gespeichert.")


if __name__ == "__main__":
    main()
