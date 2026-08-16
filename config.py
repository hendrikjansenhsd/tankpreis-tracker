"""Konfiguration für den Tankpreis-Tracker."""

# Stadtzentren (lat, lng) und Suchradius in km (API-Maximum: 25 km)
CITIES = {
    "Oberhausen": (51.4696, 6.8514, 12),
    "Essen": (51.4556, 7.0116, 12),
    "Duesseldorf": (51.2277, 6.7735, 12),
}

# Golf 5 mit "Super 95" = E10. Falls dein Auto E10 nicht verträgt: "e5".
FUEL_TYPE = "e10"

STATIONS_FILE = "stations.csv"
PRICES_FILE = "prices.csv"
