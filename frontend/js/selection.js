/**
 * Klassen für Antworten der API und zum Verarbeiten in der GUI
 */

/**
 * Wandelt relative-Media-Pfade (API-Antwort) in komplette und valide URLs um
 * @param String  Pfad aus API-JSON-Antwort (ist nur ein Teil-Pfad)
 * @return String Komplette URL des Media-Pfads
 */
function getMediaPathUrl(apiMediaPath) {
    let encodedMediaPath = encodeURI(apiMediaPath); //Encoding aller gängigen Zeichen (Leerzeichen etc.)
    encodedMediaPath = encodedMediaPath.replaceAll("#","%23"); //Das #-Zeichen extra ersetzen (nicht in "encodeURI" enthalten)
    return mediaUrl + encodedMediaPath;
}

/**
 * Sortiert anhand des "name"-Attributs (Case-Insensitive)
 * @param any  Objekt a mit "name"-Attribut
 * @param any  Objekt a mit "name"-Attribut
 * @return int 1,0,-1
 */
function sortByName(a,b) {
    return (a["name"].toLowerCase() > b["name"].toLowerCase()) ? 1 : ((b["name"].toLowerCase() > a["name"].toLowerCase()) ? -1 : 0)
}

//Track --> Generell für den Tracktable verwenden
class Track {

    /**
     * -- Konstruktor --
     * @param string   Das JSON, was von der API zurückgegeben wurde (Track)
     * @param string   Name des Künstlers
     * @param string   Name des Albums
     * @param string   Album-Cover-URL
     * @param Function Eine Funktion, die ausgeführt werden soll, wenn die Methode "show" aufgerufen wird
     */
    constructor(apiJson,artistName,albumName,albumCover,showFunction) {

        //API-Attribute
        if(apiJson["mediaPath"].includes("http://") || apiJson["mediaPath"].includes("https://")) {
            this.mediaPath = apiJson["mediaPath"];
        } else {
            //Nur mediaPath-URL berechnen, wenn mediaPath noch keine URL ist
            this.mediaPath = getMediaPathUrl(apiJson["mediaPath"]);
        }
        this.duration  = apiJson["duration"];
        this.title     = apiJson["title"];

        //Zusätzliche Attribute
        this.artist = artistName;
        this.album  = albumName;
        this.cover  = albumCover;

        this.showFunction = showFunction;
    }

    /**
     * Zeigt das Album, AudioBook etc. des Tracks an (wird bei Erstellung des Objekts eingestellt). (void - Funktion)
     */
    show() {
        this.showFunction();
    }
}



class Album {

    /**
     * -- Konstruktor --
     * @param String Das JSON, was von der API zurückgegeben wurde
     */
    constructor(apiJson) {
        this.artistId   = apiJson["artistId"];
        this.artistName = apiJson["artistName"];

        this.id         = apiJson["id"];
        this.name       = apiJson["name"];
        this.mediaPath  = getMediaPathUrl(apiJson["mediaPath"]);
        this.cover      = getMediaPathUrl(apiJson["cover"]);
        this.published  = apiJson["published"];
        this.trackCount = apiJson["trackCount"];
        this.duration   = apiJson["duration"];
    }

    /**
     * Setzt das "container"-Attribut. (void - Funktion)
     */
    setContainer() {
        this.container = new AppContainerItem(this.cover,this.name,this.published,() => { this.show(); });
    }

    /**
     * Gibt das "container"-Attribut zurück
     * @return AppContainerItem Ein "AppContainerItem"-Objekt
     */
    getContainer() {
        return this.container;
    }

    /**
     * Setzt das "tracks"-Attribut. (void - Funktion)
     * @param String Das JSON, was von der API zurückgegeben wurde
     */
    setTracks(tracksJson) {
        this.tracks = Array.from(tracksJson, track => new Track(track,this.artistName,this.name,this.cover,() => { this.show(); }));
    }

    /**
     * Zeigt das Album an. (void - Funktion)
     */
    show() {
        navigateTo("album/" + this.id);
    }
}

class Artist {

    /**
     * -- Konstruktor --
     * @param String Das JSON, was von der API zurückgegeben wurde
     */
    constructor(apiJson) {
        this.id         = apiJson["id"];
        this.name       = apiJson["name"];
        this.mediaPath  = getMediaPathUrl(apiJson["mediaPath"]);
        this.cover      = getMediaPathUrl(apiJson["cover"]);
        this.albumCount = apiJson["audioCollectionCount"];
    }

    /**
     * Setzt das "container"-Attribut. (void - Funktion)
     */
    setContainer() {
        this.container = new AppContainerItem(this.cover,this.name,"Alben: " + this.albumCount,() => { this.show(); });
    }

    /**
     * Gibt das "container"-Attribut zurück
     * @return AppContainerItem Ein "AppContainerItem"-Objekt
     */
    getContainer() {
        return this.container;
    }

    /**
     * Setzt ein extra "tracks"-Attribut, welches zum Abspielen des gesamten Artist benötigt wird. (void - Funktion)
     * @param Array Ein Array mit Track-Objekten, die dem Artist zugewiesen werden sollen
     */
    setTracks(tracksArray) {
        this.tracks = tracksArray;
    }

    /**
     * Zeigt den Artist an. (void - Funktion)
     */
    show() {
        navigateTo("artist/" + this.id);
    }
}



class AudioBook {

    /**
     * -- Konstruktor --
     * @param String Das JSON, was von der API zurückgegeben wurde
     */
    constructor(apiJson) {
        this.authorId   = apiJson["authorId"];
        this.authorName = apiJson["authorName"];

        this.id         = apiJson["id"];
        this.name       = apiJson["name"];
        this.mediaPath  = getMediaPathUrl(apiJson["mediaPath"]);
        this.cover      = getMediaPathUrl(apiJson["cover"]);
        this.published  = apiJson["published"];
        this.trackCount = apiJson["trackCount"];
        this.duration   = apiJson["duration"];

        this.blurb = apiJson["blurb"];
    }

    /**
     * Setzt das "container"-Attribut. (void - Funktion)
     */
    setContainer() {
        this.container = new AppContainerItem(this.cover,this.name,this.published,() => { this.show(); });
    }

    /**
     * Gibt das "container"-Attribut zurück
     * @return AppContainerItem Ein "AppContainerItem"-Objekt
     */
    getContainer() {
        return this.container;
    }

    /**
     * Setzt das "tracks"-Attribut. (void - Funktion)
     * @param String Das JSON, was von der API zurückgegeben wurde
     */
    setTracks(tracksJson) {
        this.tracks = Array.from(tracksJson, track => new Track(track,this.authorName,this.name,this.cover,() => { this.show(); }));
    }

    /**
     * Zeigt das AudioBook an. (void - Funktion)
     */
    show() {
        navigateTo("audiobook/" + this.id);
    }
}

class Author {

    /**
     * -- Konstruktor --
     * @param String Das JSON, was von der API zurückgegeben wurde
     */
    constructor(apiJson) {
        this.id             = apiJson["id"];
        this.name           = apiJson["name"];
        this.mediaPath      = getMediaPathUrl(apiJson["mediaPath"]);
        this.cover          = getMediaPathUrl(apiJson["cover"]);
        this.audioBookCount = apiJson["audioCollectionCount"];
    }

    /**
     * Setzt das "container"-Attribut. (void - Funktion)
     */
    setContainer() {
        this.container = new AppContainerItem(this.cover,this.name,"Hörbücher: " + this.audioBookCount,() => { this.show(); });
    }

    /**
     * Gibt das "container"-Attribut zurück
     * @return AppContainerItem Ein "AppContainerItem"-Objekt
     */
    getContainer() {
        return this.container;
    }

    /**
     * Setzt ein extra "tracks"-Attribut, welches zum Abspielen des gesamten Author benötigt wird. (void - Funktion)
     * @param Array Ein Array mit Track-Objekten, die dem Author zugewiesen werden sollen
     */
    setTracks(tracksArray) {
        this.tracks = tracksArray;
    }

    /**
     * Zeigt den Author an. (void - Funktion)
     */
    show() {
        navigateTo("author/" + this.id);
    }
}



class Channel {

    /**
     * -- Konstruktor --
     * @param String Das JSON, was von der API zurückgegeben wurde
     */
    constructor(apiJson) {
        this.id        = apiJson["id"]; 
        this.name      = apiJson["name"];
        this.mediaPath = getMediaPathUrl(apiJson["mediaPath"]);
        this.cover     = getMediaPathUrl(apiJson["cover"]);
        this.hostedBy  = apiJson["hostedBy"];
        this.tracks    = apiJson["tracks"];
        this.broadcast = apiJson["broadcast"];

        this.tracks = Array.from(this.tracks, track => new Track(track,"","",this.cover,null));
    }

    /**
     * Setzt das "container"-Attribut. (void - Funktion)
     */
    setContainer() {
        this.container = new AppContainerItem(this.cover,this.name,this.hostedBy,() => { webplayer.currentTracktable = null; webplayer.play(this); });
    }

    /**
     * Gibt das "container"-Attribut zurück
     * @return AppContainerItem Ein "AppContainerItem"-Objekt
     */
    getContainer() {
        return this.container;
    }

    /**
     * Entfernt bereits gespielte Tracks aus dem "tracks"-Array. (void - Funktion)
     */
    removePlayedTracks() {
        
        //Bereits gespielte Tracks entfernen
        if(this.broadcast["index"] > 0) {
            for(let i = 0; i < this.broadcast["index"]; i++) {
                this.tracks.shift();
            }
        }

        //Da die Tracks angepasst wurden, kann der Index auf 0 gesetzt werden
        this.broadcast["index"] = 0;
    }

    /**
     * Aktualisiert das Channel-Objekt mit neuen "tracks" und "broadcast"-Einstellungen. (void - Funktion)
     */
    async refresh() {
        let refreshed = await api.getResult("channel/id/" + this.id);

        //Refresh nur verarbeiten, wenn gültige Daten empfangen wurden
        if(refreshed.hasOwnProperty("tracks") && refreshed.hasOwnProperty("broadcast")) {

            //Neue Tracks
            this.tracks = refreshed["tracks"];
            this.tracks = Array.from(this.tracks, track => new Track(track,"","",this.cover,null));

            //Neuer Broadcast
            this.broadcast = refreshed["broadcast"];

            //Tracks entfernen, die bereits gespielt wurden
            this.removePlayedTracks();

        } else {

            //Leere Attribute
            this.tracks = [];
            this.broadcast = {};
        }
    }

    /**
     * Zeigt den Channel an (mit automatischem Scrolling). (void - Funktion)
     */
    show() {

        //Zur Channel-View navigieren, sollte diese nicht geladen sein
        if(!window.location.href.includes(getRouteWithoutParameters(10))) {
            navigateTo(getRouteWithoutParameters(10));
        }

        //Intervall zum Suchen des Channel-Elements
        var searchInterval = setInterval((() => {

            //Das "app"-DIV
            let appDiv = document.getElementById("app");

            //Prüfe, ob ein AppContainer vorhanden ist
            if(typeof appDiv.childNodes[0].classList !== 'undefined' && appDiv.childNodes[0].classList.contains("app__container_border")) {

                //NodeList in Array, damit man damit auch arbeiten kann
                let channelElements = [... appDiv.childNodes[0].childNodes];
                channelElements.splice(0,1); //Head entfernen

                //Suche das HTML-Element zum Channel heraus
                let channelElementToFocus = channelElements.find(channelElement => {

                    //Name muss stimmen (ist eindeutig)
                    if(channelElement.childNodes[1].childNodes[0].innerText === this.name) {
                        
                        //Hosts muss stimmen
                        if(channelElement.childNodes[1].childNodes[1].innerText === this.hostedBy) {
                            return true;
                        }
                    }

                });

                //Wenn das Channel-Element gefunden wurde --> Hinscrollen
                if(typeof channelElementToFocus !== 'undefined') {

                    //Channel-Element fokussieren
                    focusInApp(channelElementToFocus);

                    //Intervall beenden
                    clearInterval(searchInterval);
                }
            }

        }).bind(this),100);
    }
}



class Playlist {

    /**
     * -- Konstruktor --
     * @param String Das JSON, was von der API zurückgegeben wurde
     */
    constructor(apiJson) {
        this.id          = apiJson["id"]; 
        this.name        = apiJson["name"];
        this.mediaPath   = getMediaPathUrl(apiJson["mediaPath"]);
        this.cover       = getMediaPathUrl(apiJson["cover"]);
        
        this.published   = apiJson["published"];
        this.tracks      = apiJson["tracks"];
        this.trackCount  = apiJson["trackCount"];
        this.description = apiJson["description"];
        this.duration    = apiJson["duration"];
    }

    /**
     * Setzt das "container"-Attribut. (void - Funktion)
     */
    setContainer() {
        this.container = new AppContainerItem(this.cover,this.name,this.published,() => { this.show(); });
    }

    /**
     * Gibt das "container"-Attribut zurück
     * @return AppContainerItem Ein "AppContainerItem"-Objekt
     */
    getContainer() {
        return this.container;
    }

    /**
     * Setzt das "tracks"-Attribut. (void - Funktion)
     * @param String Das JSON, was von der API zurückgegeben wurde
     */
    setTracks(tracksJson) {
        this.tracks = Array.from(tracksJson, track => new Track(track,track["artistName"],track["albumName"],getMediaPathUrl(track["cover"]),() => { this.show(); }));
    }

    /**
     * Zeigt die Playlist an. (void - Funktion)
     */
    show() {
        navigateTo("playlist/" + this.id);
    }
}



class Podcast {

    /**
     * -- Konstruktor --
     * @param String Das JSON, was von der API zurückgegeben wurde
     */
    constructor(apiJson) {
        this.id          = apiJson["id"]; 
        this.name        = apiJson["name"];
        this.mediaPath   = getMediaPathUrl(apiJson["mediaPath"]);
        this.cover       = getMediaPathUrl(apiJson["cover"]);

        this.description  = apiJson["description"];
        this.publisher    = apiJson["publisher"];
        this.episodeCount = apiJson["episodeCount"];
    }

    /**
     * Setzt das "container"-Attribut. (void - Funktion)
     */
    setContainer() {
        this.container = new AppContainerItem(this.cover,this.name,this.publisher,() => { this.show(); });
    }

    /**
     * Gibt das "container"-Attribut zurück
     * @return AppContainerItem Ein "AppContainerItem"-Objekt
     */
    getContainer() {
        return this.container;
    }

    /**
     * Setzt das "tracks"-Attribut -> wäre "episodes" in API. (void - Funktion)
     * @param String Das JSON, was von der API zurückgegeben wurde
     */
    setEpisodes(episodesJson) {
        this.tracks = Array.from(episodesJson, episode => new Track(episode,episode["description"],this.name,this.cover,() => { this.show(); }));
    }

    /**
     * Zeigt den Podcast an. (void - Funktion)
     */
    show() {
        navigateTo("podcast/" + this.id);
    }
}