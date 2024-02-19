# Reverse Proxy Anleitung

Wenn Radiotracks auf einem öffentlichen Server läuft, muss man **Waitress** benutzen.

Dieses unterstützt leider aktuell kein HTTPs und es ist auch sonst anzuraten, vor dem WSGI-Server einen ordentlichen Webserver zu setzen. Das hat Sicherheits- und Performance-Gründe.

## Grundlegendes Setup

Es wird ein Weiterleitungsport eingestellt, der vom Webserver benutzt wird, um die Anfragen an **Waitress** weiterzuleiten. Dadurch kommen die Anfragen nicht von den Clients selbst, sondern vom Webserver.

`Client-Anfrage -> Webserver-Port -> Waitress-Port` und Antworten dann in entgegengesetzter Richtung.

In diesem Beispiel wird Port `8080` benutzt, man kann aber auch irgend einen anderen (freien) Port benutzen.

### Firewall

In der Firewall muss nach Außen hin nur der übliche Webserver-Port für das Front-End (HTTP / HTTPs) und `8080` für die Weiterleitung an **Waitress** freigegeben sein.

### settings.json

In der `settings.json` im `api`-Segment:

* `host` Einstellung auf `127.0.0.1` setzen (damit der Server nur intern erreichbar ist)
* `port` Einstellung auf `1337` setzen (wird intern auf dem Server benutzt, NICHT NACH AUßEN FREIGEBEN!)
* `production` Einstellung auf `true` setzen
* `usesReverseProxy` Einstellung auf `true` setzen
* `reverseProxyUrlScheme` Einstellung auf `http` oder `https` setzen (je nachdem, ob der Webserver auf dem Waitress-Weiterleitungsport HTTPs angeschaltet hat)

### frontend

Im Front-End müssen in der `api.js` die Variablen `apiUrl` auf HTTP oder HTTPs (je nachdem, ob der Webserver auf dem Waitress-Weiterleitungsport HTTPs angeschaltet hat) und `apiPort` auf `8080` gesetzt werden.

## Webserver

Der Webserver muss angewiesen werden die Anfragen auf dem Weiterleitungsport an **Waitress** weiterzugeben.

### Apache

Apache muss über `Listen 8080` auf dem Weiterleitungsport Verbindungen annehmen. 

Danach fügt man einen `<VirtualHost>` hinzu, der auf dem Weiterleitungsport lauscht und die Weiterleitungs-Direktiven enthält.

Je nach Betriebssystem, Distribution und Setup ist die Einstellung entweder in `httpd.conf` oder einer anderen Konfigurationsdatei vorzunehmen.

Das Resultat sollte ungefähr so aussehen:

```
<VirtualHost *:8080>

#...
#ggf. SSL bzw. HTTPs Einstellungen (Zertifikat etc.)
#...

#Modul für Proxy-Unterstützung laden, Forwarding aller Verbindungen und Header-Einstellungen
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
ProxyPass / http://127.0.0.1:1337/ connectiontimeout=5 timeout=30 #Die Angaben "connectiontimeout" und "timeout" sind optional, können aber Performance verbessern
SetEnv force-proxy-request-1.0 1    #OPTIONAL -> Waitress soll besser performen, wenn man HTTP 1.0 statt 1.1 benutzt
SetEnv proxy-nokeepalive 1          #OPTIONAL -> Waitress soll besser performen, wenn man keinen HTTP-KeepAlive benutzt
RequestHeader set X-Forwarded-Proto http
RequestHeader set X-Forwarded-Prefix /

</VirtualHost> 
```

Wichtig ist hier, dass bei `ProxyPass` die Protokollangabe immer HTTP sein sollte und nicht HTTPs, denn sonst würde die Weiterleitung selbst (bzw. deren Daten) wiedermals durch HTTPs verschlüsselt werden, was zu nicht lesbaren Übertragungen an **Waitress** führt!