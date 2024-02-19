/**
 * AudioBook-Seite
 */

class AudioBookView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - AudioBook");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {

        //AudioBook von der API abfragen
        var audioBook = await api.getResult("audiobook/id/" + this.params.id);

        //Prüfe, ob AudioBook gefunden wurde
        if(Object.keys(audioBook).length > 0) {
            audioBook = new AudioBook(audioBook);
            
            //Titel überschreiben
            this.setTitle("Radiotracks - " + audioBook.name);

            //AudioBook-Header
            var audioBookHeader = new AppContainerHeader(
                audioBook.cover,
                "Hörbuch",
                audioBook.name,
                [
                    '<a href="' + baseURL + 'author/' + audioBook.authorId + '" data-link>' + audioBook.authorName + "</a>",
                    audioBook.published,
                    audioBook.trackCount + " Tracks",
                    getWrittenOutDuration(audioBook.duration)
                ],
                () => { webplayer.play(audioBook,true); }
            );

            //Klappentext des AudioBook
            var infoContainer = new AppContainerInfo("Klappentext",audioBook.blurb);

            //Tracks der Playlist abfragen
            var audioBookTracks = await api.getResult("audiobook/tracks/id/" + this.params.id);
            audioBook.setTracks(audioBookTracks);

            //Tracktable
            var trackTable = new AppTracktable(audioBook.tracks,false,false);

            //Header, Klappentext und Tracktable in einen Container packen und diesen ausgeben
            return new AppContainer([audioBookHeader,infoContainer,trackTable],false).element;
        }

        return displayNotFound();
    }
}