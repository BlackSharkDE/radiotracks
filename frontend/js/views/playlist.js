/**
 * Playlist-Seite
 */

class PlaylistView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - Playlist");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {

        //Playlist von der API abfragen
        var playlist = await api.getResult("curatedplaylist/id/" + this.params.id);

        //Prüfe, ob Playlist gefunden wurde
        if(Object.keys(playlist).length > 0) {
            playlist = new Playlist(playlist);

            //Titel überschreiben
            this.setTitle("Radiotracks - " + playlist.name);

            //Playlist-Header
            var playlistHeader = new AppContainerHeader(
                playlist.cover,
                "Playlist",
                playlist.name,
                [
                    playlist.published,
                    playlist.trackCount + " Tracks",
                    getWrittenOutDuration(playlist.duration)
                ],
                () => { webplayer.play(playlist,true); }
            );

            //Beschreibung der Playlist
            var infoContainer = new AppContainerInfo("Beschreibung",playlist.description);

            //Tracks der Playlist abfragen
            var playlistTracks = await api.getResult("curatedplaylist/tracks/id/" + this.params.id);
            playlist.setTracks(playlistTracks);

            //Tracktable
            var trackTable = new AppTracktable(playlist.tracks,true,true);

            //Header, Info-Container und Tracktable in einen Container packen und diesen ausgeben
            return new AppContainer([playlistHeader,infoContainer,trackTable],false).element;
        }

        return displayNotFound();
    }
}