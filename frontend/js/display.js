/**
 * Weitere Dinge für das Anzeigen von Inhalten (wird als erstes eingebunden)
 */

//==================================================================================================================================================================
//-- Zeitanzeige-Formatierungen --

/**
 * Formatiert eine Dauer in Sekunden in einen Zeitstring
 * @param Int     Dauer eines Tracks in Sekunden
 * @param bool    Ob versucht werden soll, die beiden "HH"-Stellen zu entfernen
 * @return String In "HH:MM:SS" bzw. "MM:SS" formatierter String / "INFINITE", wenn Dauer unendlich ist
 */
function getDurationFormat(durationInSeconds,tryStripHours = true) {
    if(isFinite(durationInSeconds)) {

        //Format "HH:MM:SS"
        let formatted = new Date(durationInSeconds * 1000).toISOString().substr(11, 8);
        
        //Versuche die "HH"-Stellen zu entfernen
        if(tryStripHours) {
            //Wenn Dauer kleiner als eine Stunde ist => "HH" == "00" => kann entfernt werden
            //Wenn Dauer größer als eine Stunde ist  => "HH" != "00" => immer behalten
            if(durationInSeconds < 3600) {
                formatted = formatted.substring(3); //"HH:" weglassen
            }
        }
        return formatted;
    }

    return "INFINITE";
}

/**
 * Formatiert eine Dauer in Sekunden in einen Zeitstring
 * @param Int     Dauer eines Tracks in Sekunden
 * @return String Zeit im Format "xx Std. xx Min." (wenn jeweilige Einheit nicht vorhanden, wird diese weggelassen)
 */
function getWrittenOutDuration(durationInSeconds) {

    //Komplettes Format (HH:MM:SS)
    var durationFormat = getDurationFormat(durationInSeconds,false);
    
    //Entspricht "HH:MM"
    durationFormat = durationFormat.substring(0,5);

    //Rückgabe
    var writtenOut = "";

    //Stunden
    var hours = parseInt(durationFormat.substring(0,2));
    if(hours > 0) {
        writtenOut += hours.toString() + " Std. ";
    }

    //Minuten
    var minutes = parseInt(durationFormat.substring(3));
    if(minutes > 0) {
        writtenOut += minutes.toString() + " Min."
    }

    return writtenOut;
}

//==================================================================================================================================================================
//-- Bilder --

/**
 * Setzt die Hintergrundfarbe eines HTML-Elements anhand der Durchschnittsfarbe eines übergebenen Bildes. (void - Funktion)
 * 
 * Hinweise:
 * => Bei CORS-Image-Ressourcen funktioniert dies nicht -> Element-Hintergrund bleibt bei aktueller Farbe
 * => Sollte die Durchschnittsfarbe der Vergleichsfarbe zu ähnlich sein bleibt der Element-Hintergrund bei aktueller Farbe (hat keine gute, optische Wirkung)
 * 
 * @param Blob    Blob eines Bildes
 * @param Element Das DOM-Element, welches eingefärbt werden soll
 */
async function setAverageColor(imgBlob,domElement) {

    let imageFile = new File([imgBlob],"image",{type: imgBlob.type});
    let cI = new ColorfulImage(imageFile);
    cI.loadImageFile() //Promise für Laden des Bildes
    .then(
        cILoaded => {

            //Durchschnittsfarbe des Bildes berechnen
            let averageColor = cILoaded.averageColor();
            //console.log(averageColor); //DEBUG

            //Berechne den "Unterschied" der Durschnittsfarbe zur App-Div-Hintergrundfarbe
            let cD_1 = ColorfulImage.calculateColorDifference(averageColor,{r:18,g:18,b:18});
            //console.log(cD_1); //DEBUG

            //Berechne den "Unterschied" der Durschnittsfarbe zur Schriftfarbe (Weiß)
            let cD_2 = ColorfulImage.calculateColorDifference(averageColor,{r:255,g:255,b:255});
            //console.log(cD_2); //DEBUG

            //Sollte die Durschnittsfarbe der Vergleichsfarbe zu ähnlich sein, Änderung weglassen
            if(cD_1 > 2000 && cD_2 > 2000) {
                domElement.style.backgroundColor = ColorfulImage.rgbToHex(averageColor);
            }
        }
    )
    .catch(anyError => {
        //domElement.style.backgroundColor = "#ff0000"; //DEBUG => Zeigt an, dass ein Fehler passiert ist
        console.error(anyError)
    });
}

/**
 * Zeigt eine Blob-Bild-Ressource an. (void - Funktion)
 * @param Blob    Ein Image-Blob
 * @param Element Ein IMG-Element, in das das Bild geladen werden soll
 */
function displayImage(imgBlob,imageElement) {
    if(imgBlob.size > 0) {
        //-- Bild wurde richtig geladen => Normal anzeigen --
        let objectUrl = URL.createObjectURL(imgBlob);
        imageElement.src    = objectUrl; //"src" auf Blob setzen
        imageElement.onload = () => { URL.revokeObjectURL(objectUrl); }; //URL und damit Blob freigeben, wenn geladen
    } else {
        //-- Bild wurde nicht richtig geladen => Platzhalter-Bild anzeigen --
        imageElement.src = "res/placeholder.png";
    }
}

//==================================================================================================================================================================

/**
 * Fokussiert ein Element im "app"-DIV. (void - Funktion)
 * @param Element Ein HTML-/DOM-Element
 */
function focusInApp(elementToFocus) {

    //"app"-DIV
    let appDiv = document.getElementById("app");
    
    //Mittlere Höhe von "app" bestimmen
    let sectionMiddle = appDiv.offsetHeight / 2;

    //Mittlere Höhe des Elements, das fokussiert werden soll
    let elementMidHeight = elementToFocus.offsetHeight / 2;

    //Position (Y-Achse) herausfinden
    let yPosition = elementToFocus.offsetTop - (sectionMiddle - elementMidHeight);

    //Hinscrollen
    appDiv.scrollTo({top: yPosition, left: 0, behavior: 'smooth'});
}

//==================================================================================================================================================================

//Kontextmenü (Rechtsklick) navigiert zum Visualizer
window.addEventListener("contextmenu", (event) => {
    event.preventDefault();
    navigateTo(getRouteWithoutParameters(16));
});