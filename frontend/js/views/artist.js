/**
 * Artist-Seite
 */

class ArtistView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - Künstler");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {

        //Artist von der API abfragen
        var artist = await api.getResult("artist/id/" + this.params.id);

        //Prüfe, ob Artist gefunden wurde
        if(Object.keys(artist).length > 0) {
            artist = new Artist(artist);

            //Titel überschreiben
            this.setTitle("Radiotracks - " + artist.name);

            //Artist-Header
            var artistHeader = new AppContainerHeader(
                artist.cover,
                "Künstler",
                artist.name,
                [
                    "Alben: " + artist.albumCount
                ],
                async () => {

                    //Alle Tracks des Artist über alle Alben hinweg
                    let allArtistTracks = [];

                    //Die Tracks von jedem Album abfragen und setzen
                    await Promise.all(albums.map(async (album) => {
                        let albumTracks = await api.getResult("album/tracks/id/" + album.id);
                        album.setTracks(albumTracks);
                    }));

                    //Alle Tracks aller Alben zusammentragen
                    albums.forEach(album => allArtistTracks = allArtistTracks.concat(album.tracks));

                    //Tracks dem Artist zuweisen
                    artist.setTracks(allArtistTracks);

                    //Webplayer den Artist übergeben
                    webplayer.play(artist,true);
                }
            );

            //Alle Album-JSON-Objekte des Artist abfragen
            var albums = await api.getResult("artist/albums/id/" + this.params.id);

            //Albums sortieren
            albums.sort((a,b) => {

                //Zuerst anhand von "published"
                if(a.published > b.published) {
                    return 1;
                } else if(a.published < b.published) {
                    return -1;
                }

                //Dann anhand von "name" (Case-Insensitive)
                let aName = a.name.toLowerCase();
                let bName = b.name.toLowerCase();
                if(aName < bName) {
                    return -1;
                } else if(aName > bName) {
                    return 1;
                } else {
                    return 0;
                }
            });

            //Alle Album-Objekte erstellen
            albums.forEach((album, index, theArray) => {
                let albumObject = new Album(album);
                albumObject.setContainer();
                theArray[index] = albumObject;
            });

            //Alle Album-HTML-Elemente
            var albumElements = [];
            albums.forEach(album => albumElements.push(album.getContainer()));

            return new AppContainer([artistHeader].concat(albumElements)).element;
        }

        return displayNotFound();
    }
}