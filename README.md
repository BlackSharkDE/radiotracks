# Radiotracks-4

Eigenes Spotify

## Übersicht

* Das backend ist in Python implementiert und bietet allerhand Funktionen für das Frontend.
  * Datenabfrage (Artists, Authors, Channel, Playlists, Podcasts)
  * Indexierung von Audiodateien auf dem Server
  * Musik-Channel-Generierung (durchgehende Radiosender-Simulation)
  * Kuration von Playlists
  * Das Python-Package `jfiles` (nicht enthalten) dient nur für Datei- / Verzeichnisoperationen.
  * Das Python-Package `mutagen`, `mariadb`, `Flask` und `Waitress` sind Fremdmodule, die von anderen Entwicklern stammen.

* Das Frontend nutzt JavaScript und bietet ein Single-Page-Application Erlebnis (ähnlich zu anderen Frontend-Frameworks).
  * Es wurden keine Fremdbibliotheken verwendet, alles ist in nativem JS implementiert.
  * `rainbow.js` Wechselt Farbattribute durch das RGB-Sprektrum
  * `vanilla-spa.js` bietet die SPA-Funktionalität
  * `colorfulimage.js` bietet Funktionen zum Analysieren von Bildern

* Im `production`-Ordner befinden sich Notizen und Skripte für den Produktivbetrieb.