"""
Wertet die offiziellen historischen Tankerkoenig-Rohdaten aus (die taeglichen
"prices/JAHR/MONAT/JAHR-MONAT-TAG-prices.csv" Dateien aus dem Git-Dump).
Im Unterschied zu collect_prices.py/analyze.py sind das keine stuendlichen
Snapshots, sondern einzelne Preisaenderungs-Events -- dieses Skript
rekonstruiert daraus pro Tankstelle einen stuendlichen Preisverlauf
(vorwaerts aufgefuellt) und wertet den dann genauso aus wie analyze.py.

Vorbereitung:
1. stations.csv muss existieren (siehe get_stations.py)
2. Rohdaten-CSVs der gewuenschten Monate irgendwo lokal ablegen, z.B. in
   einen Ordner "raw_history/" (egal in welcher Unterordnerstruktur --
   das Skript sucht rekursiv nach *-prices.csv)

Aufruf: python historical_to_hourly.py raw_history/
"""
import glob
import sys

import pandas as pd

from config import FUEL_TYPE, STATIONS_FILE

WEEKDAYS_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

COLUMNS = ["date", "station_uuid", "diesel", "e5", "e10", "dieselchange", "e5change", "e10change"]


def load_station_ids():
    stations = pd.read_csv(STATIONS_FILE)
    return set(stations["id"])


def load_raw_files(folder):
    files = glob.glob(f"{folder.rstrip('/')}/**/*-prices.csv", recursive=True)
    if not files:
        raise SystemExit(f"Keine *-prices.csv Dateien in {folder} gefunden.")
    print(f"{len(files)} Tagesdateien gefunden, lade und filtere...")

    station_ids = load_station_ids()
    frames = []
    for path in sorted(files):
        try:
            df = pd.read_csv(path, names=COLUMNS, header=0, usecols=["date", "station_uuid", FUEL_TYPE])
        except Exception as e:
            print(f"  Ueberspringe {path}: {e}")
            continue
        df = df[df["station_uuid"].isin(station_ids)]
        if not df.empty:
            frames.append(df)

    if not frames:
        raise SystemExit("Keine passenden Zeilen fuer deine Tankstellen gefunden.")

    combined = pd.concat(frames, ignore_index=True)
    combined["date"] = pd.to_datetime(combined["date"])
    combined = combined.rename(columns={FUEL_TYPE: "price"})
    combined = combined[combined["price"] > 0]  # 0/-1 = ungueltiger Preis
    return combined.sort_values("date")


def to_hourly(df):
    """Pro Tankstelle: Change-Events -> stuendlicher Preis (vorwaerts aufgefuellt)."""
    hourly_frames = []
    for station_id, group in df.groupby("station_uuid"):
        group = group.set_index("date").sort_index()
        hourly = group["price"].resample("1h").ffill().dropna()
        hourly_frames.append(hourly.rename("price").to_frame())
    return pd.concat(hourly_frames)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Aufruf: python historical_to_hourly.py <ordner-mit-rohdaten>")
    folder = sys.argv[1]

    raw = load_raw_files(folder)
    hourly = to_hourly(raw)
    hourly["hour"] = hourly.index.hour
    hourly["weekday"] = hourly.index.dayofweek

    print(f"\n{len(hourly)} stuendliche Preispunkte rekonstruiert "
          f"({hourly.index.min().date()} bis {hourly.index.max().date()})\n")

    by_hour = hourly.groupby("hour")["price"].mean().sort_index()
    print("Durchschnittspreis je Stunde (Cent):")
    print((by_hour * 100).round(1).to_string())

    by_weekday = hourly.groupby("weekday")["price"].mean().sort_index()
    by_weekday.index = [WEEKDAYS_DE[i] for i in by_weekday.index]
    print("\nDurchschnittspreis je Wochentag (Cent):")
    print((by_weekday * 100).round(1).to_string())

    cheapest_hour = by_hour.idxmin()
    priciest_hour = by_hour.idxmax()
    print(f"\nGuenstigste Stunde im Schnitt: {cheapest_hour}:00 Uhr ({by_hour[cheapest_hour]*100:.1f} ct)")
    print(f"Teuerste Stunde im Schnitt: {priciest_hour}:00 Uhr ({by_hour[priciest_hour]*100:.1f} ct)")

    hourly.to_csv("historical_hourly_prices.csv")
    print("\nRohdaten (stuendlich, aufbereitet) gespeichert: historical_hourly_prices.csv")


if __name__ == "__main__":
    main()
