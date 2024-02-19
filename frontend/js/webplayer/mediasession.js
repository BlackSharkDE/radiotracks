/**
 * Verwaltung der Media-Session des Browsers
 */

//Statische Klasse für die MediaSession des Browsers
class MediaSession {

    /**
     * Setzt die Metadaten für Media-Session-Funktionalität. (void - Funktion)
     * @param String Aktueller Track bzw. Channelname
     * @param String Name des Artist / Channel
     * @param String Name des Albums / der Hosts des Channels
     * @param String URL zum Cover des Albums / Channels
     */
    static setMediasessionMetadata(trackName,givenArtist,givenAlbum,coverUrl) {

        //-- Media-Metadata --
        if('mediaSession' in navigator) { //Ist nicht in allen Browsern benutzbar

            coverUrl = embedCredentials(coverUrl);

            //Setzen der Mediasession-Metadata
            navigator.mediaSession.metadata = new MediaMetadata({
                title: trackName,
                artist: givenArtist,
                album: givenAlbum,
                artwork: [
                    { src: coverUrl, sizes: '96x96', type: 'image/png' },
                    { src: coverUrl, sizes: '128x128', type: 'image/png' },
                    { src: coverUrl, sizes: '192x192', type: 'image/png' },
                    { src: coverUrl, sizes: '256x256', type: 'image/png' },
                    { src: coverUrl, sizes: '384x384', type: 'image/png' },
                    { src: coverUrl, sizes: '512x512', type: 'image/png' }
                ]
            });
        }
    }

    /**
     * Setzt das Attribut "playbackState" der MediaSession. (void - Funktion)
     * @param string Kann etweder "playing" oder "paused" sein
     */
    static setMediaSessionPlaybackState(playbackState) {

        //-- Media-Metadata --
        if('mediaSession' in navigator) { //Ist nicht in allen Browsern benutzbar

            //Kann nur folgende Werte haben
            if(playbackState === "playing" || playbackState === "paused") {
                navigator.mediaSession.playbackState = playbackState;
            }
        }
    }

    /**
     * Stellt die Methoden ein, die für die Media-Keys gelten sollen. (void - Funktion)
     */
    static setMediaSessionActions() {

        //-- Media-Keys --
        if('mediaSession' in navigator) { //Ist nicht in allen Browsern benutzbar

            //Previous / Vorheriger (Media-Key)
            navigator.mediaSession.setActionHandler('previoustrack',() => { webplayer.previous(true); });

            //Next / Nächster (Media-Key)
            navigator.mediaSession.setActionHandler('nexttrack',() => { webplayer.next(true); });

            //Play (Media-Key)
            navigator.mediaSession.setActionHandler('play',() => { webplayer.playAudio(true); });

            //Pause (Media-Key)
            navigator.mediaSession.setActionHandler('pause',() => { webplayer.pauseAudio(); });
        }
    }

    /**
     * Entfernt bzw. setzt die MediaSession zurück. (void - Funktion)
     */
    static removeMediaSession() {
        navigator.mediaSession.metadata = null;
    }
}

MediaSession.setMediaSessionActions();