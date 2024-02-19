/**
 * Album-Seite
 */

class AlbumView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - Album");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {

        //Album von der API abfragen
        var album = await api.getResult("album/id/" + this.params.id);
        
        //Prüfe, ob Album gefunden wurde
        if(Object.keys(album).length > 0) {
            album = new Album(album);

            //Titel überschreiben
            this.setTitle("Radiotracks - " + album.name);

            //Album-Header
            var albumHeader = new AppContainerHeader(
                album.cover,
                "Album",
                album.name,
                [
                    '<a href="' + baseURL + 'artist/' + album.artistId + '" data-link>' + album.artistName + "</a>",
                    album.published,
                    album.trackCount + " Tracks",
                    getWrittenOutDuration(album.duration)
                ],
                () => { webplayer.play(album,true); }
            );

            //Tracks des Album abfragen
            var albumTracks = await api.getResult("album/tracks/id/" + this.params.id);
            album.setTracks(albumTracks);

            //Tracktable
            var trackTable = new AppTracktable(album.tracks,false,false);

            //Header und Tracktable in einen Container packen und diesen ausgeben
            return new AppContainer([albumHeader,trackTable],false).element;
        }

        return displayNotFound();
    }
}