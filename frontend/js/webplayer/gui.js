/**
 * Konstanten und Funktionen, um die visuelle Komponente des Players zu steuern
 */

//==================================================================================================================================================================
//-- Konstanten --

//"player__currentplay"-Elemente
const currentPlayLoading = document.getElementById("player__currentplay__loading");
const bannerElement      = document.getElementById("player__currentplay__banner__image");
const currentPlayBig     = document.getElementById("player__currentplay__big");
const currentPlaySmall   = document.getElementById("player__currentplay__small");

//Buttons des Webplayers
const randomButton    = document.getElementById("player__controls__main__random");
const previousButton  = document.getElementById("player__controls__main__previous");
const playPauseButton = document.getElementById("player__controls__main__playpause");
const nextButton      = document.getElementById("player__controls__main__next");
const loopButton      = document.getElementById("player__controls__main__loop");

//Trackmeta
const trackmetaDiv  =  document.getElementById("player__controls__trackmeta");
const currentTime   = document.getElementById("player__controls__trackmeta__currentTime");
const seekerSlider  = document.getElementById("player__controls__trackmeta__seekerslider");
const currentLength = document.getElementById("player__controls__trackmeta__currentTrackLength");

//Sound
const soundSlider = document.getElementById("player__right__volumeslider");
const muteButton  = document.getElementById("player__right__volume");

//Aktuelle Playlist
const currentPlaylist = document.getElementById("player__right__playlist");

//==================================================================================================================================================================
//-- Funktionen --

/**
 * Setzt alles im "player__currentplay"-Div. (void - Funktion)
 * @param String   URL des anzuzeigenden Banners / Covers
 * @param String   Was im großen Text stehen soll
 * @param String   Was im kleinen Text stehen soll
 * @param Function Eine Funktion, die ausgeführt werden soll, wenn auf das Bild geklickt wird
 */
function setCurrentPlay(bannerUrl,bigText,smallText,imageOnClickFunction) {
    bannerElement.src          = embedCredentials(bannerUrl);
    currentPlayBig.innerText   = bigText;
    currentPlaySmall.innerText = smallText;
    bannerElement.onclick      = imageOnClickFunction;

    //Sollte der Visualisierer bereits initialisiert worden sein, dessen Cover-Element mit aktualisieren
    if(VisualizeView_container !== null) {
        VisualizeView_container.updateCoverElement();
    }
}

/**
 * Setzt alles im "player__currentplay"-Div auf Standardwerte zurück. (void - Funktion)
 */
function resetCurrentPlay() {
    bannerElement.src          = "res/placeholder.png";
    currentPlayBig.innerText   = "";
    currentPlaySmall.innerText = "";
    bannerElement.onclick      = () => {};
}

/**
 * Zeigt die Ladeanimation im Banner an. (void - Funktion)
 */
function showCurrentPlayLoading() {

    //Ladeanimation anzeigen
    currentPlayLoading.style.visibility = "visible";

    //Aktuelles Banner durchsichtig machen
    bannerElement.style.opacity = 0.5;
}

/**
 * Versteckt die Ladeanimation im Banner. (void - Funktion)
 */
function hideCurrentPlayLoading() {

    //Ladeanimation verstecken
    currentPlayLoading.style.visibility = "hidden";

    //Aktuelles Banner nicht durchsichtig machen
    bannerElement.style.opacity = 1;
}

/**
 * Ändert die Farbe eines Buttons auf entweder rot oder weiß. (void - Funktion)
 * @param Element Button-Element
 */
function toggleButton(buttonElement) {
    //Noch nie gesetzt --> Ist weiß, also zu rot
    if(buttonElement.style.color.localeCompare("") === 0) {
        buttonElement.style.color = "#ff0000";
    } else {
        if(buttonElement.style.color.localeCompare("rgb(255, 255, 255)") == 0) { //Wenn weiß, dann rot
            setRedColor(buttonElement);
        } else if(buttonElement.style.color.localeCompare("rgb(255, 0, 0)") == 0) { //Wenn rot, dann weiß
            setWhiteColor(buttonElement);
        }
    }
}

/**
 * Setzt die Farbe eines Elements auf rot. (void - Funktion)
 * @param Element HTML/Dom-Element
 */
function setRedColor(element) {
    element.style.color = "#ff0000";
}

/**
 * Setzt die Farbe eines Elements auf weiß. (void - Funktion)
 * @param Element HTML/Dom-Element
 */
function setWhiteColor(element) {
    element.style.color = "#ffffff";
}

/**
 * Ändert den Play/Pause-Button in das jeweilige Gegenteil. (void - Funktion)
 */
function changePlayPause() {
    if(!webplayer.audio.paused) {
        //Play, dann zu Pause-Button
        playPauseButton.innerHTML = '<i class="fa fa-pause-circle"></i>';
        setRedColor(playPauseButton);
    } else {
        //Pause, dann zu Play-Button
        playPauseButton.innerHTML = '<i class="fa fa-play-circle"></i>';
        setWhiteColor(playPauseButton);
    }
}

/**
 * Versteckt das Div "trackmeta". (void - Funktion)
 */
function hideTrackmeta() {
    trackmetaDiv.style.visibility = "hidden";
}

/**
 * Zeigt das Div "trackmeta". (void - Funktion)
 */
function showTrackmeta() {
    //Da im Hintergrund (wenn Channel spielen) diese HTML-Elemente noch immer angepasst werden, diese bei wieder einschalten zurücksetzen
    currentTime.innerText   = "00:00:00";
    currentLength.innerText = "00:00:00";

    trackmetaDiv.style.visibility = "visible";
}

/**
 * Versteckt die Buttons "Loop" und "Random". (void - Funktion)
 */
function hideModifierControls() {
    loopButton.style.visibility   = "hidden";
    randomButton.style.visibility = "hidden";
}

/**
 * Zeigt die Buttons "Loop" und "Random" an. (void - Funktion)
 */
function showModifierControls() {
    loopButton.style.visibility   = "visible";
    randomButton.style.visibility = "visible";
}

/**
 * Aktualisiert die aktuelle Track-Zeit. (void - Funktion)
 */
function updateTrackmetaCurrentTime() {
    if(webplayer.audio.duration > 0) {
        //Finde das Format der Track-Dauer im "HH:MM:SS" Format heraus (immer)
        let trackDurationFormat = getDurationFormat(webplayer.audio.duration,false);
        trackDurationFormat     = trackDurationFormat.substring(0,2); //Die ersten beiden stellen ("HH")

        //Ob versucht werden soll, die "HH"-Stellen wegzunehmen
        let tryStrip = false; //Standardmäßig nein
        if(trackDurationFormat === "00") {
            //Track ist keine Stunde(n) lang -> Stunde nicht mit ausgeben
            tryStrip = true;
        }

        //Aktuelle Track-Zeit
        currentTime.innerText = getDurationFormat(webplayer.audio.currentTime,tryStrip);
    } else if(webplayer.audio.src === "") {
        //Standardwert, wenn Audio entladen wurde
        currentTime.innerText = "00:00:00";
    }
}

/**
 * Aktualisiert die aktuelle Track-Länge. (void - Funktion)
 */
function updateTrackmetaCurrentLength() {
    if(webplayer.audio.duration > 0) {
        //Wenn der Track eine gültige Länge hat, diese ausgeben
        currentLength.innerText = getDurationFormat(webplayer.audio.duration);
    } else {
        //Standardwert für andere Fälle
        currentLength.innerText = "00:00:00";
    }
}

/**
 * Aktualisiert den Seeker-Slider auf die aktuelle Track-Zeit. (void - Funktion)
 */
function updateSeekerSlider() {
    seekerSlider.value = (100 * webplayer.audio.currentTime) / webplayer.audio.duration;
}

//==================================================================================================================================================================
//-- Funktionalität den Buttons zuweisen --

//-- Buttons mitte --

randomButton.onclick = () => {

    //Gegenteilige Funktion ggf. deaktivieren
    if(webplayer.loopTrack) {
        webplayer.loopTrack = false;
        toggleButton(loopButton);
    }

    //Schalten und Button färben
    webplayer.randomTrack = !webplayer.randomTrack;
    toggleButton(randomButton);
}

previousButton.onclick = () => {
    webplayer.previous(true);
};

playPauseButton.onclick = () => {

    //Nur ausführen, wenn ein Track geladen ist
    if(webplayer.audio.src.localeCompare("") !== 0) {
        if(webplayer.audio.paused) {
            webplayer.playAudio(true);
        } else {
            webplayer.pauseAudio();
        }
    }
};

nextButton.onclick = () => {
    webplayer.next(true);
};

loopButton.onclick = () => {

    //Gegenteilige Funktion ggf. deaktivieren
    if(webplayer.randomTrack) {
        webplayer.randomTrack = false;
        toggleButton(randomButton);
    }

    //Schalten und Button färben
    webplayer.loopTrack = !webplayer.loopTrack;
    toggleButton(loopButton);
};

//-- Controls mittig (Trackmeta) --

seekerSlider.oninput = () => {
    let newTime = (seekerSlider.value * webplayer.audio.duration) / 100;

    //Ungültige Werte abfangen
    if(newTime > webplayer.audio.duration) {
        newTime = webplayer.audio.duration;
    } else if(newTime < 0) {
        newTime = 0;
    } else if(isNaN(newTime)) {
        newTime = 0;
    }

    webplayer.audio.currentTime = newTime;
};

//-- Buttons rechts --

currentPlaylist.onclick = () => {
    if(window.location.href.includes(getRouteWithoutParameters(15))) {
        //Wenn schon in "currentplaylist", dann zur Bibliothek
        navigateTo(getRouteWithoutParameters(3));
    } else {
        //Wenn noch nicht in "currentplaylist", dann dorthin
        navigateTo(getRouteWithoutParameters(15));
    }
};

muteButton.onclick = () => { 
    webplayer.muteUnmute();
    if(webplayer.audio.muted) {
        muteButton.innerHTML = '<i class="fa fa-volume-off">';
    } else {
        muteButton.innerHTML = '<i class="fa fa-volume-up">';
    }
};

soundSlider.oninput = () => { webplayer.updateVolume(); };