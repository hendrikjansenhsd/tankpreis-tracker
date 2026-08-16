"""
Erzeugt eine interaktive HTML-Karte mit allen Tankstellen aus
stations_ranked.csv. Jede Tankstelle wird als Marker mit dem
Durchschnittspreis (Zahl) angezeigt, eingefaerbt von gruen (guenstig)
bis rot (teuer).

Voraussetzung: vorher `python cheapest_stations.py` ausfuehren, das
erzeugt stations_ranked.csv.

Aufruf: python stations_map.py
"""
import branca.colormap as cm
import folium
import pandas as pd

RANKED_FILE = "stations_ranked.csv"
OUTPUT_FILE = "tankstellen_karte.html"


def main():
    df = pd.read_csv(RANKED_FILE)
    df["price_cent"] = df["avg_price"] * 100

    colormap = cm.LinearColormap(
        colors=["#2ecc71", "#f1c40f", "#e74c3c"],  # gruen -> gelb -> rot
        vmin=df["price_cent"].min(),
        vmax=df["price_cent"].max(),
        caption="Durchschnittspreis E10 (Cent/Liter)",
    )

    center_lat, center_lng = df["lat"].mean(), df["lng"].mean()
    m = folium.Map(location=[center_lat, center_lng], zoom_start=11, tiles="cartodbpositron")

    for _, row in df.iterrows():
        price = row["price_cent"]
        color = colormap(price)
        label = f"{price:.1f}"

        html = f"""
        <div style="
            background-color:{color};
            border-radius:14px;
            padding:3px 7px;
            font-size:11px;
            font-weight:bold;
            color:#1a1a1a;
            border:1.5px solid white;
            box-shadow:0 1px 3px rgba(0,0,0,0.4);
            white-space:nowrap;
        ">{label}</div>
        """

        folium.Marker(
            location=[row["lat"], row["lng"]],
            icon=folium.DivIcon(html=html, icon_size=(0, 0), icon_anchor=(20, 10)),
            popup=folium.Popup(
                f"<b>{row['name']}</b><br>{row['brand']}<br>{row['street']}, {row['place']}"
                f"<br><br>&Oslash; {price:.1f} ct/L<br>({int(row['n_messungen'])} Messungen)",
                max_width=250,
            ),
        ).add_to(m)

    colormap.add_to(m)
    m.save(OUTPUT_FILE)
    print(f"Karte gespeichert: {OUTPUT_FILE} -- Datei im Finder doppelklicken oder im Browser oeffnen.")


if __name__ == "__main__":
    main()
