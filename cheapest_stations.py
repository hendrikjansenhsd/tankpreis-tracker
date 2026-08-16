"""
Ermittelt die guenstigsten und teuersten Tankstellen basierend auf den
bisher gesammelten Daten in prices.csv -- sowohl im Durchschnitt ueber
den gesamten Sammelzeitraum als auch fuer den aktuellsten Zeitpunkt.

Aufruf: python cheapest_stations.py [--top 15]
"""
import argparse

import pandas as pd

from config import PRICES_FILE, STATIONS_FILE


def load_data():
    prices = pd.read_csv(PRICES_FILE, parse_dates=["timestamp_utc"])
    prices = prices[prices["status"] == "open"].copy()
    prices["price"] = pd.to_numeric(prices["price"], errors="coerce")
    prices = prices.dropna(subset=["price"])
    stations = pd.read_csv(STATIONS_FILE)
    return prices, stations


def fmt_row(row, price_col="avg_price"):
    extra = f"  [n={row['n_messungen']}]" if "n_messungen" in row else ""
    return f"{row[price_col]*100:5.1f} ct  {row['name']} ({row['brand']}), {row['street']}, {row['place']}{extra}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=15)
    args = parser.parse_args()

    prices, stations = load_data()

    avg = (
        prices.groupby("station_id")["price"]
        .agg(avg_price="mean", n_messungen="count")
        .reset_index()
    )
    ranked = avg.merge(stations, left_on="station_id", right_on="id").sort_values("avg_price")

    print(f"Datenzeitraum: {prices['timestamp_utc'].min()} bis {prices['timestamp_utc'].max()}")
    print(f"({prices['timestamp_utc'].nunique()} Erhebungszeitpunkte je Tankstelle)\n")

    print(f"=== {args.top} guenstigste Tankstellen im Schnitt ===")
    for _, row in ranked.head(args.top).iterrows():
        print(fmt_row(row))

    print(f"\n=== {args.top} teuerste Tankstellen im Schnitt ===")
    for _, row in ranked.tail(args.top).iloc[::-1].iterrows():
        print(fmt_row(row))

    # Momentaufnahme: guenstigste beim letzten Sammel-Lauf
    latest_ts = prices["timestamp_utc"].max()
    latest = prices[prices["timestamp_utc"] == latest_ts].merge(
        stations, left_on="station_id", right_on="id"
    ).sort_values("price")
    print(f"\n=== Guenstigste beim letzten Lauf ({latest_ts}) ===")
    for _, row in latest.head(args.top).iterrows():
        print(fmt_row(row, price_col="price"))

    ranked.to_csv("stations_ranked.csv", index=False)
    print("\nVolle Rangliste (alle Tankstellen) gespeichert: stations_ranked.csv")


if __name__ == "__main__":
    main()
