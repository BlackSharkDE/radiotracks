# vanilla-spa.js

Ein simples SPA-Framework, welches auf Standard-JavaScript basiert.

## Inspiration

Der Hauptteil des Quellcodes stammt vom YouTuber [dcode](https://www.youtube.com/@dcode-software) und seinen beiden Videos:

* [(Part 1) Build a Single Page Application with JavaScript (No Frameworks)](https://www.youtube.com/watch?v=6BozpmSjk-Y)
* [(Part 2) Adding Client Side URL Params - Build a Single Page Application with JavaScript (No Frameworks)](https://www.youtube.com/watch?v=OstALBk-jTc)

Ich habe den Quellcode dokumentiert und so umgeschrieben, sodass er einfach in neue Projekte zu inkludieren ist.

## Verwendung / Einbindung

Für ein umfangreiches Beispiel siehe `index.html`.

## Routen bzw. Unter-URLs direkt ansurfen

Dafür benötigt der jeweilige Webserver eine Einstellung, um die entsprechenden URLs auf die `index.html` umzuleiten.
Bedenken sollte man dabei, dass statische Dateien, wie Bilder oder `.css` oder andere `.js`-Dateien etc. von dieser Umleitung
ausgenommen werden sollten.

Beispiel einer `.htaccess` für den Apache-Webserver ([Quelle](https://blog.pshrmn.com/single-page-applications-and-the-server/))
für die Demo:
```
#Rewrite-Engine benutzen (um Requests umzuleiten)
RewriteEngine On

#Basis-URL-Prefix (MIT / AM ENDE!)
RewriteBase /vanilla-spa.js/

#Wenn der Request direkt zur "index.html" geht, mit dieser Antworten
RewriteRule ^index.html$ - [L] #- => keine Abänderung des Pfads | [L] => Last ; rewrite hier beenden

#Wenn Request-Path kein valider Dateiname ist, rewrite fortsetzen
RewriteCond %{REQUEST_FILENAME} !-f

#Wenn Request-Path kein valides Verzeichnis, rewrite fortsetzen
RewriteCond %{REQUEST_FILENAME} !-d

#-- Wenn bis hier abgearbeitet, mit der "index.html" antworten --
RewriteRule . /vanilla-spa.js/index.html [L]
```