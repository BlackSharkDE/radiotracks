# production

Tools und Notizen für den Gebrauch von Radiotracks im produktivem Betrieb.

## MariaDB / MySQL

Man sollte auf Unix-Systemen unbeding in der `settings.json` den `host` der Datenbank auf `localhost` setzen. Dann wird bei Verbindungen zur Datenbank, statt einen neuen Socket für die Datenbankverbindung zu erstellen, direkt versucht auf den bestehenden Socket der Datenbankinstanz zuzugreifen (auch wenn ein `port` angegeben wurde). Das spart Sockets und Performance.

## Passwortgesicherte Frontend Deployments

Sollte das Frontend von Radiotracks auf einem Webserver mit Passwortschutz (HTTP-Basic-Auth) liegen, kann man sich einem kleinen Trick bedienen, der die allgemeine Bedienung wieder vereinfacht. Man sollte in der Datei `frontend/js/api.js` die Konstante `mediaUrl` so einstellen, dass bei jedem Request von Medien (Cover, Audio-Dateien etc.) ein User mitsamt Passwort mitgegeben wird (ist ein natives HTTP-Feature), der auf dem Webserver entsprechenden Zugriff hat.

Dazu die `mediaUrl` ungefähr so einstellen: `http://maxmuster:geheimespasswort@192.168.178.18/Radiotracks-4`

## convertAlbum.py

Benötigt das Python-Package `pyffmpeg`. Zur Benutzung, siehe `-- Konfiguration --` im Skript.

## delete_wav_files.bat

Simple Batch-Datei, die Dateien mit einer bestimmten Dateiendung löscht. Zur Benutzung siehe Kommentare im Skript.

## podcastDownloader.py

Benötigt die Python-Packages `requests` und `emoji`. Zudem wird die **GooglePodcastApi** benötigt. Zur Benutzung, siehe `-- Konfiguration --` im Skript.