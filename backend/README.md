# backend

## Voraussetzungen

Python mit folgenden Modulen installiert:

* **jfiles**
* **mariadb**
* **mutagen**
* **Flask**
* **Waitress**

Weiteres:

* Datenbankserver (MySQL / MariaDB)

## Einrichtung

Es muss lediglich die `settings.json` ausgefüllt werden. Dann beim ersten Start den Indexer manuell laufen lassen.

Danach kann man in der Datei `curating/curator.py` die Kurator-Funktionen für die Playlists mappen (`selectorMapping`).

## Startparameter

Um alle Optionen zu sehen `main.py` mit dem Startparameter `-h` bzw. `--help` starten.