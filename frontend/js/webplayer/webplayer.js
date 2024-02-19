/**
 * Die Logik für das Abspielen und Managen von Audio bzw. dem Webplayer
 */

class Player {

    /**
     * Initialisiert das Audio-Element/Attribut der Klasse. (void - Funktion)
     */
    initializeAudioElement() {

        //Audio-Element
        this.audio = document.createElement("audio");

        this.audio.onended = () => {
            //-- Wenn Wiedergabe zuende ist --

            /**
             * Bei Verbindungsabbrüchen bzw. wenn der Buffer für die Audio-Datei leer ist, wird das "currentTime"-Attribut
             * vom Audio-Element automatisch auf den Wert von "duration" gesetzt.
             * 
             * Daher muss unterschieden werden, wann das Event regulär ausgelöst wurde und wann nicht.
             */

            //Verhindere "ungültige" Events bzw. nur wenn kein Verbindungsabbruch passiert / alles normal ist
            if(!this.stalledOrErrorOccured) {
                //-- Steuervariable für Netzwerkprobleme ist nicht gesetzt --
                //console.log("ended->next (stalledOrErrorOccured = false)"); //DEBUG
                this.next();
            } else {
                //-- Steuervariable für Netzwerkprobleme ist gesetzt (Problem/kein normales geendet) --
                //console.log("ended->else (stalledOrErrorOccured = true)"); //DEBUG

                //Ladeanimation anzeigen (Audio hat geendet und es wird kein next ausgeführt)
                showCurrentPlayLoading();

                //Das "ended"-Event hat ausgelöst und es wurde "stalledOrErrorOccured" gesetzt
                this.endedOccured = true;
            }
        };
        this.audio.ontimeupdate = () => {
            //-- Wenn Audio-Attribut "currentTime" geändert wurde --

            //Update des Seeker-Slider
            updateSeekerSlider();

            //Update Trackmeta-CurrentTime
            updateTrackmetaCurrentTime();

            //Solange Track noch nicht zuende ist und abspielt, die aktuelle Track-Zeit zwischenspeichern
            if(this.audio.currentTime < this.audio.duration && !this.audio.paused) {
                this.playedUntil = this.audio.currentTime;
            }
        };
        this.audio.onloadedmetadata = () => {
            //-- Wenn die Metadaten für das Audio geladen sind --

            //Update Trackmeta-CurrentTime 
            updateTrackmetaCurrentTime();

            //Update Trackmeta-CurrentLength
            updateTrackmetaCurrentLength();
        };
        this.audio.onplaying = () => {
            //-- Wenn das Audio (wieder) abspielt --
            //console.log("playing (again)"); //DEBUG

            //Ladeanimation verstecken (Audio spielt (wieder))
            hideCurrentPlayLoading();

            //Wenn das "endedOccured"-Flag gesetzt ist (zurücksetzen der Steuervariablen bei Netzwerkprobleme)
            if(this.endedOccured) {
                this.stalledOrErrorOccured = false;
                this.endedOccured          = false;
            }
        };

        //-- Wenn Probleme während der Wiedergabe auftauchen --

        this.audio.onstalled = () => {
            //-- Wenn der Browser versucht Media-Daten zu laden aber keine Daten vorhanden sind --
            //console.log("stalled occured"); //DEBUG

            //Verhindere Mehrfachauslösung
            if(!this.stalledOrErrorOccured) {

                //Setze Steuervariable für Netzwerkprobleme
                this.stalledOrErrorOccured = true;

                //Pausiere Audio (da sowieso nicht weitergespielt werden kann)
                this.pauseAudio();

                //Ladeanimation anzeigen (Audio hat angehalten)
                showCurrentPlayLoading();
            }
        };
        this.audio.onerror = () => {
            //-- Wenn ein Fehler während des Ladens des Audios auftritt --
            //console.log(this.audio.error); //DEBUG (welcher Audio-Fehler direkt)

            //Verhindere Mehrfachauslösung
            if(!this.stalledOrErrorOccured) {

                //Setze Steuervariable für Netzwerkprobleme
                this.stalledOrErrorOccured = true;

                //Pausiere Audio (da ein Fehler aufgetreten ist)
                this.pauseAudio();

                //Ladeanimation anzeigen (Audio hat angehalten)
                showCurrentPlayLoading();
            }
        };
    }

    /**
     * -- Konstruktor --
     */
    constructor() {

        //Das Audio-Element initialisieren
        this.initializeAudioElement();

        //Beinhaltet die Tracks
        this.playlist = [];

        //Aktuelle Tracknummer (Index in der Playlist)
        this.currentTrack = 0;

        //Letzte Tracknummer (Index in der Playlist)
        this.previousTrack = 0;

        //Ob der aktuelle Track gelooped werden soll
        this.loopTrack = false;

        //Ob aus der Playlist ein zufälliger Track als nächstes abgespielt werden soll
        this.randomTrack = false;

        //Das Objekt, welches gerade abgespielt wird
        this.currentObject = null;

        //Aktueller Tracktable
        this.currentTracktable = null;

        //Variablen für Fehler mit Netzwerkverbindung (werden global in Klasse benötigt)
        this.stalledOrErrorOccured = false; //Ob das "stalled" und/oder "error"-Event während der aktuellen Wiedergabe ausgelöst wurde
        this.endedOccured          = false; //Ob das "ended"-Event während der aktuellen Wiedergabe ausgelöst wurde und es ein Problem gab
        this.playedUntil           = -1;    //Bis welche Sekunde der Track bereits abgespielt wurde

        //Interval, der die Audio-Netzwerkverbindung checkt (endet nicht)
        this.audioNetworkStateWatchInterval = setInterval(() => { this.audioNetworkStateWatch(); },2000);
    }

    /**
     * Prüft den Netzwerk-Status über das Audio-Element und handelt entsprechend bei Fehlern. (void - Funktion)
     */
    audioNetworkStateWatch() {

        /**
         * 0 = NETWORK_EMPTY     - Audio wurde noch nicht initialisiert
         * 1 = NETWORK_IDLE      - Audio ist aktiv und hat eine Ressource ausgewählt aber benutzt nicht die Netzwerkverbindung
         * 2 = NETWORK_LOADING   - Browser downloaded/buffert Daten (wieder) / kann auch passieren, wenn Track neu startet
         * 3 = NETWORK_NO_SOURCE - Keine Audio-Ressource gefunden
         *     => Wenn Ende von aktueller Datei und/oder neue Datei geladen werden soll, aber keine neue Datei geladen werden kann
         */
        let networkState = this.audio.networkState;

        /**
         * 0 = HAVE_NOTHING      - no information whether or not the audio/video is ready
         * 1 = HAVE_METADATA     - metadata for the audio/video is ready
         * 2 = HAVE_CURRENT_DATA - data for the current playback position is available, but not enough data to play next frame/millisecond
         * 3 = HAVE_FUTURE_DATA  - data for the current and at least the next frame is available
         * 4 = HAVE_ENOUGH_DATA  - enough data available to start playing
         */
        let readyState = this.audio.readyState;

        //DEBUG (aktueller Status von Netzwerk und Audio)
        //console.log("networkState: " + networkState + " | readyState: " + readyState);

        if((networkState == 1 && readyState == 2) || networkState == 3 || networkState == 0) {
            //-- Lade Track neu/nach (Nicht aktiv, zu wenig Daten um fortzufahren) --
            //console.log("trying to load track"); //DEBUG
            this.audio.load();
        }

        if((networkState == 1 || networkState == 2) && readyState >= 3) { //chrome: 3, firefox: 4
            //-- Versuche die Audiowiedergabe fortzusetzen --

            //Wenn Audio pausiert ist und ein Problem mit dem Netzwerk vorliegt
            if(this.audio.paused && this.stalledOrErrorOccured) {
                //console.log("trying to continue playing at " + this.playedUntil); //DEBUG

                //Je nachdem, was für ein Objekt gerade abgespielt wird
                if(this.currentObject instanceof Channel) {
                    this.play(this.currentObject); //Damit Channels einen Refresh machen
                } else {
                    this.audio.currentTime = this.playedUntil; //Track auf letzten Sekundenstand setzen
                    this.playAudio(); //Audio abspielen
                }
            }
        }
    }

    /**
     * Setzt das "src"-Attribut vom "audio"-Attribut. (void - Funktion)
     * @param string URL zur Audio-Datei
     */
    setAudioSource(urlToAudioSource) {
        urlToAudioSource = embedCredentials(urlToAudioSource);
        this.audio.src = urlToAudioSource;
    }

    /**
     * Ändert das Attribut "currentTrack" so um, sodass "previousTrack" gespeichert wird. (void - Funktion)
     * @param int Neuer Track-Index in der Playlist
     */
    changeCurrentTrack(newTrackIndex) {
        this.previousTrack = this.currentTrack;
        this.currentTrack  = newTrackIndex;
    }

    /**
     * Zeigt das Equaliser-GIF im aktuell gesetzten Tracktable. (void - Funktion)
     */
    showTracktableEqualiser() {
        
        //Wenn ein Tracktable gesetzt ist
        if(this.currentTracktable !== null) {
            
            //Equaliser-GIF aus letzten Eintrag in Tracktable entfernen
            this.currentTracktable.unsetPlayingGif(this.previousTrack);

            //Equaliser-GIF im neuen Eintrag in Tracktable anzeigen
            this.currentTracktable.setPlayingGif(this.currentTrack);
        }
    }

    /**
     * Fokussiert den aktuellen Track im aktuell gesetzten Tracktable. (void - Funktion)
     */
    focusTrack() {

        //Wenn ein Tracktable gesetzt ist und die aktuelle Playlist-View angezeigt wird
        if(this.currentTracktable !== null && window.location.href.includes(getRouteWithoutParameters(15))) {

            //Aktuellen Track fokussieren
            this.currentTracktable.focusRow(this.currentTrack);
        }
    }

    /**
     * Stellt einen Track aus der Player-Playlist zum Abspielen ein. (void - Funktion)
     * @param int  Index in "this.playlist"
     * @param int  Sekunden im Track, ab wann gestartet werden soll (OPTIONAL)
     * @param bool Ob Audio direkt abgespielt werden soll (OPTIONAL)
     */
    setupTrack(indexInPlaylist,startSeconds = 0, startAudio = true) {

        //Verhindere ungültige Indexangabe
        if(indexInPlaylist >= 0 && indexInPlaylist < this.playlist.length) {

            //Neues Audio laden
            this.setAudioSource(this.playlist[indexInPlaylist].mediaPath);
            this.changeCurrentTrack(indexInPlaylist);

            //Zurücksetzen für neuen Track (Variablen für Fehler mit Netzwerkverbindung)
            this.stalledOrErrorOccured = false;
            this.endedOccured          = false;
            this.playedUntil           = -1;

            //Audio-Start
            if(startSeconds > 0) {
                this.audio.currentTime = startSeconds;
            }

            //Informationen ändern
            if(this.currentObject instanceof Channel) {
                setCurrentPlay(this.currentObject.cover,this.currentObject.name,this.currentObject.hostedBy,() => { this.currentObject.show(); });
                MediaSession.setMediasessionMetadata(this.currentObject.name,this.currentObject.hostedBy,null,this.currentObject.cover);
            } else {
                let ct = this.playlist[this.currentTrack];
                setCurrentPlay(ct.cover,ct.title,ct.album,() => { ct.show(); });
                MediaSession.setMediasessionMetadata(ct.title,ct.artist,ct.album,ct.cover);
            }

            //Equaliser-GIF setzen
            this.showTracktableEqualiser();

            //Track fokussieren
            this.focusTrack();

            //Wenn was abgespielt wurde
            if(startAudio) {
                this.playAudio();
            }

        } else {
            //-- Wenn Index-Angabe fehlerhaft ist --

            //Verhindere Mehrfachauslösung
            if(!this.stalledOrErrorOccured) {

                //Notification anzeigen
                showNotification("Konnte keinen Track setzen!",0,true);

                //Ladeanimation anzeigen (Audio hat angehalten)
                showCurrentPlayLoading();

                //Setze Steuervariable für Netzwerkprobleme
                this.stalledOrErrorOccured = true;

                //Setze Audio auf pausiert (da ein Fehler aufgetreten ist)
                this.pauseAudio();
            }
        }
    }

    /**
     * Stellt ein Objekt zum Abspielen ein. (void - Funktion)
     * @param Object Ein Objekt, das abgespielt werden soll
     * @param bool   Ob automatisch zur aktuellen Playlist navigiert werden soll (funktioniert nicht bei Channeln) (OPTIONAL)
     */
    async play(objectToPlay,navigateToCurrentplaylist = false) {

        //Ladeanimation anzeigen
        showCurrentPlayLoading();

        //Wenn schon was spielt, dies pausieren
        this.pauseAudio();

        //Übergebenes Objekt speichern
        this.currentObject = objectToPlay;

        //ggf. neue Playlist setzen
        if(this.currentObject.hasOwnProperty("tracks")) {
            this.playlist = this.currentObject.tracks;
            
            //Zurücksetzen der Index-Werte
            this.previousTrack = 0;
            this.currentTrack  = 0;
        }

        if(this.currentObject instanceof Channel) {

            //Steuerelemente einstellen
            hideTrackmeta();
            hideModifierControls();

            //Channel aktualisieren
            await this.currentObject.refresh();

            //Wenn gültige Track-Liste und kein Internet-Channel
            if(this.currentObject.tracks.length > 0 && this.currentObject.tracks[0].duration > 0) {
                this.playlist = this.currentObject.tracks; //Die Playlist muss aktualisiert werden, da sich der Channel aktualisiert hat
                this.setupTrack(this.currentObject.broadcast["index"],this.currentObject.broadcast["start"]);
            } else {
                this.setupTrack(0);
            }

            //Zeige den Channel an
            this.currentObject.show();

        } else {

            //Steuerelemente einstellen
            showTrackmeta();
            showModifierControls();

            this.setupTrack(this.currentTrack);

            //ggf. zur aktuellen Playlist navigieren
            if(navigateToCurrentplaylist) {
                navigateTo(getRouteWithoutParameters(15));
            }
        }
    }

    /**
     * Spielt den aktuellen Track ab. (void - Funktion)
     * @param bool Ob die Funktion manuell ausgeführt wird
     */
    async playAudio(manualAction = false) {
        if(webplayer.audio.paused) {

            //Wenn Channel und manuelle Aktion (muss pausiert gewesen sein)
            if(this.currentObject instanceof Channel && manualAction === true) {

                //Audio erst einmal stummschalten --> Soll nicht zu hören sein, bis die Broadcastsimulation angewandt wurde
                this.audio.muted = true;

                //Channel erneut abfragen (Broadcast besorgen / updaten)
                await this.currentObject.refresh();

                //Playlist aktualisieren
                this.playlist = this.currentObject.tracks;

                //Wenn gültige Track-Liste und kein Internet-Channel --> Broadcast setzen
                if(this.currentObject.tracks.length > 0 && this.currentObject.tracks[0].duration > 0) {

                    //Aktuellen Track setzen (ahmt "setupTrack" nach, weil ansonsten Endlosschleife)
                    this.currentTrack      = this.currentObject.broadcast["index"];
                    this.setAudioSource(this.playlist[this.currentTrack].mediaPath);
                    this.audio.currentTime = this.currentObject.broadcast["start"];
                }

                //Wenn die neue/aktualisierte Playlist des Players leer ist
                if(this.playlist.length == 0) {
                    showNotification("Channel konnte nicht aktualisiert werden!",0,true);
                    return; //Methode vorzeitig verlassen
                }

                //Audio wieder anschalten
                this.audio.muted = false;
            }

            webplayer.audio.play();
            changePlayPause();
            MediaSession.setMediaSessionPlaybackState("playing");
        }
    }

    /**
     * Pausiert den aktuellen Track. (void - Funktion)
     */
    pauseAudio() {
        if(!this.audio.paused) {
            this.audio.pause();
            changePlayPause();
            MediaSession.setMediaSessionPlaybackState("paused");
        }
    }

    /**
     * Setzt den vorherigen Track aus der Playlist. (void - Funktion)
     * @param bool Ob die Funktion manuell ausgeführt wird
     */
    async previous(manualAction = false) {
        
        //Nur wenn Playlist nicht leer ist
        if(this.playlist.length > 0) {

            if(this.currentObject instanceof Channel && manualAction === true) {
                //-- Next-Channel --

                //Nächsten Channel von API abfragen
                let previousChannel = await api.getResult("channel/previous/id/" + this.currentObject.id);

                //Wenn API-Rückgabe gültig ist
                if(Object.keys(previousChannel).length > 0) {
                    //Neuen Channel erstellen und abspielen
                    previousChannel = new Channel(previousChannel);
                    this.play(previousChannel);
                } else {
                    showNotification("Vorheriger Channel konnte nicht abgerufen werden!",0,true);
                }

                //Nichts weiter ausführen
                return;
            } else {
                //-- Normaler Track etc. --

                //Vorheriger Track-Index
                let prevTrack = 0;

                if(this.loopTrack && !manualAction) {
                    //-- Loop --
                    prevTrack = this.currentTrack;
                } else if(this.randomTrack) {
                    //-- Random --
                    prevTrack = this.previousTrack;
                } else {
                    //Einfach vorherigen Track aus Playlist laden
                    prevTrack = this.currentTrack - 1;

                    //Zu niedrigen Index abfangen
                    if(prevTrack < 0) {
                        prevTrack = this.playlist.length - 1;
                    }
                }

                //Neuen Track setzen
                this.setupTrack(prevTrack);
            }
        }
    }

    /**
     * Setzt den nächsten Track aus der Playlist. (void - Funktion)
     * @param bool Ob die Funktion manuell ausgeführt wird
     */
    async next(manualAction = false) {

        //Nur wenn Playlist nicht leer ist
        if(this.playlist.length > 0) {

            //Nächster Track-Index
            var nextTrack = 0;

            if(this.currentObject instanceof Channel && manualAction === true) {
                //-- Next-Channel --

                //Nächsten Channel von API abfragen
                let nextChannel = await api.getResult("channel/next/id/" + this.currentObject.id);

                //Wenn API-Rückgabe gültig ist
                if(Object.keys(nextChannel).length > 0) {
                    //Neuen Channel erstellen und abspielen
                    nextChannel = new Channel(nextChannel);
                    this.play(nextChannel);
                } else {
                    showNotification("Nächster Channel konnte nicht abgerufen werden!",0,true);
                }

                //Nichts weiter ausführen
                return;
            } else if(this.currentObject instanceof Channel && manualAction === false) {
                //-- Nächster Track im Channel --

                //Gerade gespielten Channel-Track entfernen
                this.playlist.shift();

                //Teste, ob noch Tracks für den Channel geladen sind
                if(this.playlist.length === 0) {
                    //-- Keine Tracks mehr -> nachholen --

                    //Channel aktualisieren
                    await this.currentObject.refresh();

                    //Playlist aktualisieren
                    this.playlist = this.currentObject.tracks;
                }

                //Wieder am Anfang der Playlist anfangen
                nextTrack = 0;

            } else {
                //-- Normaler Track etc. --

                if(this.loopTrack && !manualAction) {
                    //-- Loop --
                    nextTrack = this.currentTrack;
                } else if(this.randomTrack) {
                    //-- Random --
                    nextTrack = Math.floor(Math.random() * this.playlist.length - 1);
                    if(nextTrack < 0) {
                        nextTrack = 0;
                    }
                } else {
                    //Einfach nächsten Track aus Playlist laden
                    nextTrack = this.currentTrack + 1;

                    //Zu hohen Index abfangen
                    if(nextTrack > (this.playlist.length - 1)) {
                        nextTrack = 0;
                    }
                }
            }

            //Neuen Track setzen
            this.setupTrack(nextTrack);
        }
    }

    /**
     * Aktualisiert die Lautstärke vom Audio. (void - Funktion)
     */
    updateVolume() {
        this.audio.volume = soundSlider.value / 100; //Umrechnen in Float (Volume muss zwischen 0.0 und 1.0 sein)
    }

    /**
     * Schaltet Sound an/aus. (void - Funktion)
     */
    muteUnmute() {
        this.audio.muted = !this.audio.muted;
    }

    /**
     * Fügt ein "Track"-Objekt der Playlist hinzu
     * @param Track Ein Track-Objekt
     */
    addTrackToPlaylist(trackObj) {
        
        //Sollte aktuell ein Channel abgespielt werden, diesen entfernen
        if(this.currentObject instanceof Channel) {
            this.playlist = [];
        }

        this.playlist.push(trackObj); //Neuen Track in Playlist speichern
        this.changeCurrentTrack(this.playlist.length - 1); //Auf aktuellsten Track stellen
        this.play(this.playlist[this.currentTrack]); //Aktuellsten Track abspielen
    }

    /**
     * Entfernt die aktuelle Playlist. (void - Funktion)
     */
    deletePlaylist() {

        //Funktioniert nur, wenn gerade kein Channel spielt und die Playlist nicht leer ist
        if(!(this.currentObject instanceof Channel) && this.playlist.length > 0) {
            
            //Wenn gerade etwas abgespielt wird, pausieren
            if(!this.audio.paused) {
                this.pauseAudio();
            }

            //Aktuelles Audio entladen => Audio-Element neu initialisieren (besitzt keine "src"-URL)
            this.initializeAudioElement();

            //Playlist leeren
            this.playlist = [];

            //Tracktable zurücksetzen
            this.currentTracktable = null;

            //Volume neu vom Volume-Slider übernehmen
            this.updateVolume();

            //Informationen (CurrentPlay-DIV) zurücksetzen
            resetCurrentPlay();

            //MediaSession zurücksetzen
            MediaSession.removeMediaSession();

            //Reset der Trackmeta-CurrentTime
            updateTrackmetaCurrentTime();

            //Reset der Trackmeta-CurrentLength
            updateTrackmetaCurrentLength();

            //Reset des Seeker-Slider
            updateSeekerSlider();

            //Zurück zur Hauptseite
            navigateTo(getRouteWithoutParameters(0));
        } else {
            showNotification("Playlist ist bereits leer");
        }
    }
}

//==================================================================================================================================================================

//Statische Variable, die den Player enthält
const webplayer = new Player();