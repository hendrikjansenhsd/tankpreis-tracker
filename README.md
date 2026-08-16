# Tankpreis-Tracker: Oberhausen, Essen, Düsseldorf

Sammelt 8 Wochen lang stündlich E10-Preise aller Tankstellen in den drei
Städten und wertet danach aus, zu welchen Uhrzeiten/Wochentagen günstig
getankt werden kann. Läuft komplett kostenlos über GitHub Actions – dein
eigener Rechner muss dafür nicht laufen.

## 1. API-Key besorgen (5 Minuten)

1. Gehe auf **https://onboarding.tankerkoenig.de** und fülle das Formular
   aus (Name, E-Mail).
2. Du bekommst den Key per E-Mail zugeschickt. Kostenlos, keine Kreditkarte
   nötig.

## 2. GitHub-Repository anlegen

1. Neues Repository auf github.com erstellen, z. B. `tankpreis-tracker`
   (privat ist ok, siehe Hinweis unten zu Actions-Minuten).
2. Alle Dateien aus diesem Ordner in das Repository hochladen (per
   GitHub-Weboberfläche "Add file" → "Upload files", oder per `git push`).

## 3. API-Key als Secret hinterlegen

Im Repository: **Settings → Secrets and variables → Actions → New repository
secret**
- Name: `TANKERKOENIG_API_KEY`
- Value: dein Key aus Schritt 1

## 4. Tankstellen einmalig ermitteln

Lokal auf deinem Rechner (nur dieser eine Schritt braucht deinen PC):

```bash
pip install -r requirements.txt
export TANKERKOENIG_API_KEY="dein-key"
python get_stations.py
```

Das erzeugt `stations.csv`. Diese Datei per `git add stations.csv`,
`git commit`, `git push` ins Repository hochladen — sie ist die Grundlage
für die stündliche Preisabfrage.

## 5. Automatik aktivieren

Der Workflow (`.github/workflows/collect.yml`) startet automatisch jede
Stunde, sobald die Datei im Repo liegt. Zum Testen: im Reiter **Actions**
den Workflow "Tankpreise sammeln" öffnen und **Run workflow** klicken —
danach sollte eine `prices.csv` im Repo erscheinen.

**Hinweis zu privaten Repos:** GitHub Actions ist für private Repos auf
2.000 Freiminuten/Monat begrenzt. Ein stündlicher Lauf (~1 Min pro Lauf,
~720 Läufe/Monat) passt locker rein. Falls du auf Nummer sicher gehen
willst oder mehr Tankstellen abfragst, mach das Repo stattdessen **public**
— dort ist es komplett unlimitiert. Die Daten sind ja nicht sensibel.

## 6. Nach 8 Wochen: Auswertung

```bash
git pull   # aktuelle prices.csv holen
python analyze.py
```

Gibt dir Durchschnittspreise je Stunde/Wochentag in der Konsole aus und
erzeugt `tankpreis_analyse.png` mit Liniendiagramm + Heatmap.

## Sofort-Auswertung mit historischen Daten (ohne 8 Wochen zu warten)

Die Tankerkönig-Historie reicht bis 2014 zurück – du kannst schon jetzt mit
den letzten Wochen arbeiten, statt auf den eigenen Sammler zu warten.

**Voraussetzung:** Gleicher Account wie für den API-Key, aber der Zugriff
auf das Git-Repo muss zusätzlich freigeschaltet werden (Registrierung unter
https://onboarding.tankerkoenig.de, danach ggf. kurze Prüfung durch
Tankerkönig).

**Daten holen – zwei Wege:**

**A) Einfach per Browser (kein Git nötig):**
Auf https://dev.azure.com/tankerkoenig/_git/tankerkoenig-data zu den
Ordnern `prices/2026/07` und `prices/2026/08` navigieren und dort jeweils
"Download as Zip" nutzen. Enthält alle deutschen Tankstellen, aber nur
diese zwei Monate – das sind schon die gewünschten letzten ~6-8 Wochen.

**B) Per Git (nur relevante Ordner, kein 65-GB-Clone):**
```bash
git clone --filter=blob:none --no-checkout https://tankerkoenig@dev.azure.com/tankerkoenig/tankerkoenig-data/_git/tankerkoenig-data
cd tankerkoenig-data
git sparse-checkout init --cone
git sparse-checkout set prices/2026/07 prices/2026/08
git checkout master   # ggf. "main", je nachdem was `git branch -a` zeigt
```

**Auswerten:**
```bash
python get_stations.py        # falls noch nicht geschehen -> stations.csv
python historical_to_hourly.py pfad/zu/den/entpackten/prices-ordnern
```

Gibt dir dieselbe Stunden-/Wochentags-Auswertung wie `analyze.py`, nur
sofort statt nach 8 Wochen. Der Live-Sammler läuft trotzdem sinnvoll
parallel weiter, falls sich die Preisdynamik durch die neue 12-Uhr-Regel
seit April 2026 nochmal ändert.

## Dateien im Überblick

| Datei | Zweck |
|---|---|
| `config.py` | Städte, Radius, Kraftstoffsorte (aktuell E10) |
| `get_stations.py` | Einmalig: Tankstellen-Liste erzeugen |
| `collect_prices.py` | Stündlich (per Actions): Preise abfragen |
| `analyze.py` | Nach 8 Wochen: Auswertung + Chart (eigene Live-Daten) |
| `historical_to_hourly.py` | Sofort: Auswertung aus offiziellen historischen Rohdaten |
| `.github/workflows/collect.yml` | Der Cronjob |
