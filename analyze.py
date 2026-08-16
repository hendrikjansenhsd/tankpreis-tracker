"""
Auswertung von prices.csv: durchschnittlicher Preis je Uhrzeit und Wochentag.
Lokal ausfuehren, nachdem genug Daten gesammelt wurden.

Aufruf: python analyze.py
"""
import matplotlib.pyplot as plt
import pandas as pd

from config import FUEL_TYPE, PRICES_FILE

WEEKDAYS_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]


def load_data():
    df = pd.read_csv(PRICES_FILE, parse_dates=["timestamp_utc"])
    df = df[df["status"] == "open"].copy()
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])

    # UTC -> Europe/Berlin fuer korrekte lokale Uhrzeit/Wochentag
    df["timestamp_local"] = df["timestamp_utc"].dt.tz_convert("Europe/Berlin")
    df["hour"] = df["timestamp_local"].dt.hour
    df["weekday"] = df["timestamp_local"].dt.dayofweek  # 0=Montag
    return df


def main():
    df = load_data()
    print(f"{len(df)} Preispunkte geladen ({FUEL_TYPE})\n")

    by_hour = df.groupby("hour")["price"].mean().sort_index()
    print("Durchschnittspreis je Stunde (Cent):")
    print((by_hour * 100).round(1).to_string())

    by_weekday = df.groupby("weekday")["price"].mean().sort_index()
    by_weekday.index = [WEEKDAYS_DE[i] for i in by_weekday.index]
    print("\nDurchschnittspreis je Wochentag (Cent):")
    print((by_weekday * 100).round(1).to_string())

    cheapest_hour = by_hour.idxmin()
    priciest_hour = by_hour.idxmax()
    print(f"\nGuenstigste Stunde im Schnitt: {cheapest_hour}:00 Uhr ({by_hour[cheapest_hour]*100:.1f} ct)")
    print(f"Teuerste Stunde im Schnitt: {priciest_hour}:00 Uhr ({by_hour[priciest_hour]*100:.1f} ct)")

    # Heatmap: Wochentag x Stunde
    pivot = df.pivot_table(values="price", index="weekday", columns="hour", aggfunc="mean") * 100
    pivot.index = [WEEKDAYS_DE[i] for i in pivot.index]

    fig, axes = plt.subplots(2, 1, figsize=(11, 9))

    axes[0].plot(by_hour.index, by_hour.values * 100, marker="o")
    axes[0].set_title(f"Durchschnittlicher {FUEL_TYPE.upper()}-Preis nach Uhrzeit")
    axes[0].set_xlabel("Stunde")
    axes[0].set_ylabel("Preis (Cent/L)")
    axes[0].set_xticks(range(0, 24))
    axes[0].grid(True, alpha=0.3)

    im = axes[1].imshow(pivot.values, aspect="auto", cmap="RdYlGn_r")
    axes[1].set_yticks(range(len(pivot.index)))
    axes[1].set_yticklabels(pivot.index)
    axes[1].set_xticks(range(len(pivot.columns)))
    axes[1].set_xticklabels(pivot.columns)
    axes[1].set_xlabel("Stunde")
    axes[1].set_title("Preis-Heatmap: Wochentag x Uhrzeit (rot = teurer)")
    fig.colorbar(im, ax=axes[1], label="Cent/L")

    plt.tight_layout()
    plt.savefig("tankpreis_analyse.png", dpi=150)
    print("\nChart gespeichert: tankpreis_analyse.png")


if __name__ == "__main__":
    main()
