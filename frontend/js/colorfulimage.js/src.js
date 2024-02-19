/**
 * colorfulimage.js
 * 
 * Farbanalyse von Bildern
 */

class ColorfulImage {

    /**
     * -- Konstruktor --
     * @param File Ein File-Objekt (z.B. aus <input>-Tag mit dem type="file" oder ein geladenes BLOB als File)
     */
    constructor(fileObject) {
        this.file      = fileObject;
        this.image     = undefined; //Image-Objekt => Siehe "loadImageFile"
        this.imageData = undefined; //ImageData-Objekt => Siehe "loadImageFile"
        this.rgbArray  = [];        //Array mit RBG-Daten => Siehe "setRgbArray" 
        this.quantization = [];     //Reduziertes "rgbArray" => Siehe "setQuantization"
    }

    /**
     * Lädt die Bilddatei / Vorbereitung für weiteres. (void - Funktion)
     * @return Promise Ein Promise, welches bei resolve das Objekt selbst beinhaltet oder bei reject eine DOMException
     */
    loadImageFile() {
        return new Promise((resolve,reject) => {

            //Lädt die Datei
            const temporaryFileReader = new FileReader();

            //Bei Fehler
            temporaryFileReader.onerror = () => {
                temporaryFileReader.abort();
                reject(new DOMException("Problem parsing input file."));
            };

            //Sobald das Bild geladen wurde
            temporaryFileReader.onload = () => {

                //Für wenn das Bild eingelesen wurde
                this.image = new Image();

                //Sobald das Bild selbst geladen ist
                this.image.onload = () => {

                    //Erstelle ein <canvas>-Element im Arbeitesspeicher, welches dazu benutzt wird die Bild-Daten zu berechnen
                    const canvas = document.createElement("canvas");
                    canvas.width = this.image.width;
                    canvas.height = this.image.height;
                    const ctx = canvas.getContext("2d");
                    ctx.drawImage(this.image,0,0);

                    //Attribut "imageData" setzen
                    this.imageData = ctx.getImageData(0,0,canvas.width,canvas.height);

                    //resolve(temporaryFileReader.result);
                    resolve(this);
                }

                //Fehler beim Laden des Bildes
                this.image.onerror = () => {
                    reject(new DOMException("Problem loading image file."));
                }

                this.image.src = temporaryFileReader.result;

                if(this.image.complete) {
                    //-- Sollte das Bild bereits im Cache sein, das "onload"-Event manuell triggern
                    this.image.dispatchEvent(new Event("load"));
                }
            }

            //Liest die Datei als binär-Daten ein und encoded diese als base64-url
            temporaryFileReader.readAsDataURL(this.file);
        });
    }

    //-- Internes --

    /**
     * Konvertiert ein RGBA-Array in ein RGB-Array
     * @param Array  Das "data"-Attribut des "imageData"-Attributs
     * @return Array Ein RGB-Array
     */
    buildRgbArray(dataFromImage) {

        //Rückgabe
        let rgbValues = [];

        //Alle 4 Einträge eine Zusammenfassung erstellen
        //=> dataFromImage besteht aus RGBA-Werten und sieht so z.B. so aus: [23,255,12,255,60,  200,123,255,45,76  ...]
        //=> Es gehören dann in der Sequenz immer 4 Werte zu einem RGBA-Wert
        for(let i = 0; i < dataFromImage.length; i += 4) {
            let rgb = {
                r: dataFromImage[i],
                g: dataFromImage[i + 1],
                b: dataFromImage[i + 2],
            };
            rgbValues.push(rgb);
        }

        return rgbValues;
    }

    /**
     * Findet den größten Unterschied/Spannweite zwischen den Min- und Max-Werten von den RGB-Werten
     * @return String Farbwert mit dem größten Unterschied: "r" oder "g" oder "b"
     */
    findBiggestColorRange(rgbValues) {

        /**
         * Min-Werte werden mit den Maximalwerten initialisiert, damit
         * das Minimum für den jeweiligen Farbkanal gefunden werden kann
         *
         * Max-Werte werden mit den Minimalwerten initialisiert, damit
         * das Maximum für den jeweiligen Farbkanal gefunden werden kann
         */

        let rMin = Number.MAX_VALUE;
        let gMin = Number.MAX_VALUE;
        let bMin = Number.MAX_VALUE;

        let rMax = Number.MIN_VALUE;
        let gMax = Number.MIN_VALUE;
        let bMax = Number.MIN_VALUE;

        rgbValues.forEach((pixel) => {
            rMin = Math.min(rMin, pixel.r);
            gMin = Math.min(gMin, pixel.g);
            bMin = Math.min(bMin, pixel.b);

            rMax = Math.max(rMax, pixel.r);
            gMax = Math.max(gMax, pixel.g);
            bMax = Math.max(bMax, pixel.b);
        });

        //Unterschied/Spannweiten berechnen
        const rRange = rMax - rMin;
        const gRange = gMax - gMin;
        const bRange = bMax - bMin;

        //Finde Farbkanal mit dem/der größten Unterschied/Spannweite
        const biggestRange = Math.max(rRange, gRange, bRange);
        if(biggestRange === rRange) {
            return "r";
        } else if(biggestRange === gRange) {
            return "g";
        } else {
            return "b";
        }
    }

    /**
     * Implementation vom "Median cut"-Algorithmus zum Reduzieren der Daten
     * @param Array  Das "rgbArray"-Attribut bzw. Kopie davon
     * @param int    Tiefe (wie viele Farben bei 2er-Potenz)
     * @return Array Reduziertes Array
     */
    medianCut(rgbValues,depth) {

        const MAX_DEPTH = 4;

        //-- Standardfall abfangen --
        //=> Gewünschte Tiefe erreicht ODER Array leer (beendet Rekursion)
        if(depth === MAX_DEPTH || rgbValues.length === 0) {

            let color = rgbValues.reduce(
                (prev,curr) => {
                    prev.r += curr.r;
                    prev.g += curr.g;
                    prev.b += curr.b;

                    return prev;
                },
                {
                    r: 0,
                    g: 0,
                    b: 0,
                }
            );

            color.r = Math.round(color.r / rgbValues.length);
            color.g = Math.round(color.g / rgbValues.length);
            color.b = Math.round(color.b / rgbValues.length);

            return [color];
        }

        //-- Andernfalls --

        /**
         *  Rekursiv folgendes tun:
         *  1. Finde den Farbkanal (r/g/b) mit der größten Spannweite
         *  2. Nach dem Farbkanal aus 1 sortieren
         *  3. RGB-Array halbieren
         *  4. Wiederhole bis Standardfall eintritt
         */
        let componentToSortBy = this.findBiggestColorRange(rgbValues);

        rgbValues.sort((p1, p2) => {
            return p1[componentToSortBy] - p2[componentToSortBy];
        });

        let mid = rgbValues.length / 2;
        return [
            ...this.medianCut(rgbValues.slice(0, mid), depth + 1),
            ...this.medianCut(rgbValues.slice(mid + 1), depth + 1),
        ];
    }

    //-- Kann erst ausgeführt werden, nachdem "loadImageFile" ausgeführt wurde --

    /**
     * Setzt das "rgbArray"-Attribut. (void - Funktion)
     */
    setRgbArray() {
        this.rgbArray = this.buildRgbArray(this.imageData.data);
    }

    /**
     * Setzt das "quantization"-Attribut. (void - Funktion)
     */
    setQuantization() {
        this.quantization = this.medianCut([...this.rgbArray],0);
    }

    /**
     * Gibt die Durchschnittsfarbe im Bild zurück
     * @return Object Ein Objekt mit dem RGB-Wert
     */
    averageColor() {

        //Nur jeden 5ten Pixel berücksichtigen
        let blockSize = 5;

        let i = -4;
        let length = 0;
        let rgb = {r:0,g:0,b:0};
        let count = 0;
        
        length = this.imageData.data.length;

        while((i += blockSize * 4) < length ) {
            ++count;
            rgb.r += this.imageData.data[i];
            rgb.g += this.imageData.data[i+1];
            rgb.b += this.imageData.data[i+2];
        }

        //~~ zum abrunden
        rgb.r = ~~(rgb.r/count);
        rgb.g = ~~(rgb.g/count);
        rgb.b = ~~(rgb.b/count);

        return rgb;
    }

    /**
     * Gibt die dominate Farbe im Bild zurück
     * @return Object Ein Objekt mit dem RGB-Wert
     */
    dominantColor() {

        //<canvas>-Element im Arbeitsspeicher, welches für die Berechnung genutzt wird
        const canvas  = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width  = this.image.width;
        canvas.height = this.image.height;

        //Bild ganz klein (1px * 1px) zeichnen
        context.drawImage(this.image, 0, 0, 1, 1);
    
        //Farbe besorgen (wird über Kleinscalierung durch das Canvas ermittelt)
        let dC = context.getImageData(0, 0, 1, 1).data;

        return {
            r: dC[0],
            g: dC[1],
            b: dC[2]
        }
    }

    //-- Funktionen für externe Aufrufe --

    /**
     * Ordnet mittels relativer Leuchtkraft die Helligkeit der Farben
     * @param Array  Das "rgbArray"-Attribut bzw. Kopie davon
     * @return Array Neu sortiertes Array
     */
    static orderByLuminance(rgbValues) {
        
        //Funktion für Helligkeitsberechnung
        const calculateLuminance = (p) => {
            return 0.2126 * p.r + 0.7152 * p.g + 0.0722 * p.b;
        };

        //Sortierung
        return rgbValues.sort((p1, p2) => {
            return calculateLuminance(p2) - calculateLuminance(p1);
        });
    }

    /**
     * Konvertiert ein Array mit RGB-Werte in HSL-Werte
     * @param Array   Das "rgbArray"-Attribut bzw. Kopie davon
     * @return Object Ein Objekt mit HSL-Werten
     */
    static convertRGBtoHSL(rgbValues) {
        return rgbValues.map((pixel) => {

            let hue = 0;
            let saturation = 0;
            let luminance = 0;

            //Skala von 0-255 auf 0 - 1 ändern
            let redOpposite   = pixel.r / 255;
            let greenOpposite = pixel.g / 255;
            let blueOpposite  = pixel.b / 255;

            const Cmax = Math.max(redOpposite, greenOpposite, blueOpposite);
            const Cmin = Math.min(redOpposite, greenOpposite, blueOpposite);

            const difference = Cmax - Cmin;

            luminance = (Cmax + Cmin) / 2.0;

            if (luminance <= 0.5) {
                saturation = difference / (Cmax + Cmin);
            } else if (luminance >= 0.5) {
                saturation = difference / (2.0 - Cmax - Cmin);
            }

            /**
             * Wenn R max, dann Hue = (G-B)/(max-min)
             * Wenn G max, dann Hue = 2.0 + (B-R)/(max-min)
             * Wenn B max, dann Hue = 4.0 + (R-G)/(max-min)
             */
            const maxColorValue = Math.max(pixel.r, pixel.g, pixel.b);

            if (maxColorValue === pixel.r) {
                hue = (greenOpposite - blueOpposite) / difference;
            } else if (maxColorValue === pixel.g) {
                hue = 2.0 + (blueOpposite - redOpposite) / difference;
            } else {
                hue = 4.0 + (greenOpposite - blueOpposite) / difference;
            }

            //Finde den Sektor (jeweils 60 Grad) zu dem die Farbe gehört
            hue = hue * 60;

            //Muss immer ein positiver Winkel sein
            if (hue < 0) {
                hue = hue + 360;
            }

            //Wenn R und G und B gleich sind => Neutrale Farbe (weiß, grau, schwarz)
            if (difference === 0) {
                return false;
            }

            return {
                h: Math.round(hue) + 180, //Plus 180 Grad, weil das ist die Komplementärfarbe
                s: parseFloat(saturation * 100).toFixed(2),
                l: parseFloat(luminance * 100).toFixed(2),
            };
        });
    }

    /**
     * Wandelt eine RGB-Farbe in hexadezimale Schreibweise um
     * @param Entry   Ein Objekt aus "rgbArray"- oder "quantization"-Attribut
     * @return String Hexadezimale Schreibweise des Wertes
     */
    static rgbToHex(pixel) {
        const componentToHex = (c) => {
            const hex = c.toString(16);
            return hex.length == 1 ? "0" + hex : hex;
        };
        
        return (
            "#" +
            componentToHex(pixel.r) +
            componentToHex(pixel.g) +
            componentToHex(pixel.b)
        ).toUpperCase();
    }

    /**
     * Wandelt einen HSL-Wert in eine hexadezimale Schreibweise um
     * @param Entry   Ein Objekt aus "rgbArray"- oder "quantization"-Attribut
     * @return String Hexadezimale Schreibweise des Wertes
     */
    static hslToHex(hslColor) {
        const hslColorCopy = { ...hslColor };
        hslColorCopy.l /= 100;
        const a = (hslColorCopy.s * Math.min(hslColorCopy.l, 1 - hslColorCopy.l)) / 100;

        const f = (n) => {
            const k = (n + hslColorCopy.h / 30) % 12;
            const color = hslColorCopy.l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
            return Math.round(255 * color).toString(16).padStart(2,"0");
        };

        return `#${f(0)}${f(8)}${f(4)}`.toUpperCase();
    }

    /**
     * Berechnet die Farb-Distanz bzw. Unterschied zwischen zwei Farben
     * @param Entry   Ein Objekt aus "rgbArray"- oder "quantization"-Attribut
     * @param Entry   Ein Objekt aus "rgbArray"- oder "quantization"-Attribut
     * @return Number Distanz zwischen den Farben
     */
    static calculateColorDifference(color1,color2) {
        /**
         * Hinweis: Diese Methode ist nicht ganz akkurat
         * 
         * für bessere Resultate müsste man eine Delta-E-Distanz-Metrik nutzen
         */

        const rDifference = Math.pow(color2.r - color1.r, 2);
        const gDifference = Math.pow(color2.g - color1.g, 2);
        const bDifference = Math.pow(color2.b - color1.b, 2);

        return rDifference + gDifference + bDifference;
    }
}