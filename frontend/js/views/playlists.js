/**
 * Playlists-Seite
 */

class PlaylistsView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - Playlists");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {

        //Alle Playlist-JSON-Objekte von der API abfragen
        var playlists = await api.getResult("curatedplaylist/all");

        //Prüfe, ob Antwort nicht leer
        if(Object.keys(playlists).length > 0) {
            let containerHead = new AppContainerHead("Alle Playlists");

            //Playlists anhand der Namen sortieren
            playlists.sort(sortByName);
            
            //Alle Playlist-HTML-Elemente
            var playlistElements = [];
            playlists.forEach(playlist => {
                let playlistObject = new Playlist(playlist);
                playlistObject.setContainer();
                playlistElements.push(playlistObject.getContainer());
            });

            return new AppContainer([containerHead].concat(playlistElements)).element;
        }

        return displayNotFound();
    }
}