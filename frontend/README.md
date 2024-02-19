# frontend

## Voraussetzungen

*  **Font Awesome 4**-Bezugsquelle
*  **rainbow.js** --> Git Submodule
*  **vanilla-spa.js** --> Git Submodule
*  **colorfulimage.js** --> Git Submodule

### Font Awesome 4

Die Bezugsquelle ist aktuell auf einen selbstgehosteten Server eingestellt. Sollte man die Quelle ändern wollen, muss man in der `index.html` im `<head>` die CSS-Datei-URL
von `font-awesome.min.css` manuell abändern.

### API-Einstellungen

Die Einstellungen befinden sich in der Datei `js/connection.js`.

### SPA-Einstellungen

Da Radiotracks **vanilla-spa.js** benutzt, müssen hier ein Paar Dinge beachtet werden.

#### Base-URL

Es muss das `<base>`-Tag in der `index.html` im `<head>` angepasst werden.

#### Modifikation des Webservers

Der Webserver muss URLs im Radiotracks-Pfad immer auf `index.html` umleiten. Genaueres dazu siehe **vanilla-spa.js**.

## Testing (manuell ausführen)

Dies betrifft die Komponenten des Frontends und wie sie sich bei bestimmten Fehlern verhalten sollten.

All diese Tests sollten am besten in mehreren Browsern durchgeführt werden (Firefox, Chrome, Safari).

### Verbindungsabbrüche während Wiedergaben

Der Ausdruck **Netz weg/da** meint, dass das Netzwerk ausfällt, dann das Audio stoppt/abbricht und danach erst das Netzwerk wieder hergestellt ist.

* Für Tracks (betrifft Albums, Audiobooks, Playlists, Podcasts zugleich)
  * Langer Track (einzeln), Netz weg/da: Sollte normal fortsetzen, wo abgebrochen
  * Langer Track, Langer Track, Netz weg/da: Sollte aktuellen Track fortsetzen, wo abgebrochen
  * Album, Track 1 (sollte zuende spielen können), Netz weg/da: Wenn Track 1 zuende, sollte auf 2 wechseln und bleiben bis Netz wieder da ist.
* Channel allgemein (sollten immer einen Refresh des Channels machen und fortsetzen)
  * LightChannel, Netz weg/da
  * LightChannel 1, LightChannel 2, Netz weg, LightChannel 1, Netz da => Prüfung auf bereits gebufferte Dateien
  * InternetChannel, Netz weg/da
  * AdvancedChannel, Netz weg/da
  * AdvancedChannel, Netz weg, Playlist leer (muss Nachschub holen), Netz da
  * AdvancedChannel 1, AdvancedChannel 2, Netz weg, AdvancedChannel 1, Netz da => Prüfung auf bereits gebufferte Dateien
  * Neu auf Channel-Seite, Netz weg, Channel, Netz da => prüfen mit Light-, Advanced- und InternetChannel
  * Channel 1, Netz weg, Channel 2 => Prüfen mit Click, Next- und Previous-Buttons. Dies jeweils wenn Audio noch spielt und wenn Audio bereits abgebrochen

### Verbindungsabbrüche während Navigation

Alle Seiten (Sidebar und Unterseiten der Bibliothek, außer aktuelle Playlist und Bibliothek selbst) sollten Fehlermeldungen und eine Notification anzeigen.