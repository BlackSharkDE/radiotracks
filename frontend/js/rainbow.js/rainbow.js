/**
 * rainbow.js
 * 
 * Wechselt ein CSS-Farbattribut durch das gesamte RGB-Spektrum
 */

class RainbowObject {

    /**
     * -- Konstruktor --
     * @param HTMLElement Das HTML-Element, dessen Farbe sich ändern soll
     * @param String      CSS-Attribut, das verändert werden soll (CSS-Name, beispielsweise "border-color")
     * @param Int         Intervall in Millisekunden (OPTIONAL)
     * @param String      Startfarbe des Regenbogens (Hexadezimalwert) (OPTIONAL)
     */
    constructor(hE,cA,fT = 10,sC = "#ff0000") {

        //Übergabeparameter speichern
        this.htmlElement  = hE;
        this.cssAttribute = cA;
        this.fadeTime     = fT;
        this.startColor   = sC;

        //Zählt mit, bei welcher Regenbogenkombi das Skript aktuell ist
        this.rainbowIndex = 0;

        //Ob das CSS-Attribut schon gesetzt wurde (erster Start)
        this.rainbowStartColorSet = false;

        //Enthält das Objekt der "setInterval"-Funktion
        this.interval = null;
    }

    /**
     * Startet den Farbwechsel (void - Funktion)
     */
    startRainbow() {
        this.interval = setInterval(function() {
            this.rainbow();
        }.bind(this),this.fadeTime);
    }

    /**
     * Stoppt den Farbwechsel (void - Funktion)
     */
    stopRainbow() {
        clearInterval(this.interval);
        this.rainbowStartColorSet = false; //Falls das Attribut bis zum nächsten Start geändert wird
    }

    /**
     * Ändert die Farbe (void - Funktion)
     */
    rainbow() {

        //Das CSS-Attribut muss beim ersten Aufruf gesetzt werden
        if(!this.rainbowStartColorSet) {
            this.htmlElement.style.setProperty(this.cssAttribute,this.startColor);
            this.rainbowStartColorSet = true;
        }

        //DEBUG
        //console.log(htmlElement);

        //Gibt einen String zurück: rgb(R-Wert,G-Wert,B-Wert)
        var rgb = this.htmlElement.style.getPropertyValue(this.cssAttribute); //Suche aktuellen RGB-Wert heraus (einfach von einem Element nehmen, da eh alle gleiche Farbe haben)
        //console.log("ALTES RGB: " + rgb); //DEBUG

        //RGB-String aufsplitten, sodass die RGB-Werte ausgelesen werden können
        rgb = rgb.substring(4, rgb.length-1).replace(/ /g, '').split(','); //Erklärung: / /g ersetzt alle Leerzeichen

        //Werte abspeichern
        var r = parseInt(rgb[0]);
        var g = parseInt(rgb[1]);
        var b = parseInt(rgb[2]);

        //RGB-Werte setzen
        if(this.rainbowIndex <= 255) {

            r = 255;
            g += 1;
            b = 0;

            this.rainbowIndex ++;

        } else if(this.rainbowIndex > 255 && this.rainbowIndex <= 510) {

            r -= 1;
            g = 255;
            b = 0;

            this.rainbowIndex ++;

        } else if(this.rainbowIndex > 510 && this.rainbowIndex <= 765) {

            r = 0;
            g = 255;
            b += 1;

            this.rainbowIndex ++;

        } else if(this.rainbowIndex > 765 && this.rainbowIndex <= 1020) {

            r = 0;
            g -= 1;
            b = 255;

            this.rainbowIndex ++;

        } else if(this.rainbowIndex > 1020 && this.rainbowIndex <= 1275) {

            r += 1;
            g = 0;
            b = 255;

            this.rainbowIndex ++;

        } else if(this.rainbowIndex > 1275 && this.rainbowIndex <= 1530) {

            r = 255;
            g = 0;
            b -= 1;

            this.rainbowIndex ++;

        } else {
            this.rainbowIndex = 0;
        }

        //Neuen RGB-String bauen
        rgb = "rgb(" + r + "," + g + "," + b + ")";
        //console.log("Neues RGB: " + rgb); //DEBUG

        //Neues RGB zuweisen
        this.htmlElement.style.setProperty(this.cssAttribute,rgb);
    }
}