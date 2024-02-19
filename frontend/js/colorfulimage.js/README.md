# colorfulimage.js

Farbanalyse von Bildern

Quellen:

* [Basis für Klasse](https://dev.to/producthackers/creating-a-color-palette-with-javascript-44ip)
* [averageColor - Methode](https://stackoverflow.com/questions/2541481/get-average-color-of-image-via-javascript)
* [dominantColor - Methode](https://gist.github.com/tomasdev/cf5a547290a14d829bdace43a5b0621a)

## Beispiel

```javascript
//... Bild-Daten in File-Objekt geladen
const file = File(imgData);

//Neues Objekt erstellen
let colorfulImage = new ColorfulImage(file);

//Laden der Bilddatei für die Analyse (Promise)
await colorfulImage.loadImageFile();

//Weitere Methoden siehe Abschnitt nach "loadImageFile"
```