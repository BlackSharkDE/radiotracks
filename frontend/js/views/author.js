/**
 * Author-Seite
 */

class AuthorView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - Autor");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {
        
        //Author von der API abfragen
        var author = await api.getResult("author/id/" + this.params.id);

        //Prüfe, ob Author gefunden wurde
        if(Object.keys(author).length > 0) {
            author = new Author(author);

            //Titel überschreiben
            this.setTitle("Radiotracks - " + author.name);

            //Author-Header
            var authorHeader = new AppContainerHeader(
                author.cover,
                "Autor",
                author.name,
                [
                    "Hörbücher: " + author.audioBookCount
                ],
                async () => {

                    //Alle Tracks des Author über alle Audio-Books hinweg
                    let allAuthorTracks = [];

                    //Die Tracks von jedem AudioBook abfragen und setzen
                    await Promise.all(audioBooks.map(async (audioBook) => {
                        let audioBookTracks = await api.getResult("audiobook/tracks/id/" + audioBook.id);
                        audioBook.setTracks(audioBookTracks);
                    }));

                    //Alle Tracks aller Alben zusammentragen
                    audioBooks.forEach(audioBook => allAuthorTracks = allAuthorTracks.concat(audioBook.tracks));

                    //Tracks dem Author zuweisen
                    author.setTracks(allAuthorTracks);

                    //Webplayer den Author übergeben
                    webplayer.play(author,true);
                }
            );

            //Alle Audio-Book-JSON-Objekte des Author abfragen
            var audioBooks = await api.getResult("author/audiobooks/id/" + this.params.id);

            //Audio-Books anhand der Namen sortieren
            audioBooks.sort((a,b) => {

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

            //Alle AudioBook-Objekte erstellen
            audioBooks.forEach((audioBook, index, theArray) => {
                let audioBookObject = new AudioBook(audioBook);
                audioBookObject.setContainer();
                theArray[index] = audioBookObject;
            });

            //Alle Audio-Book-HTML-Elemente
            var audioBookElements = [];
            audioBooks.forEach(audioBook => audioBookElements.push(audioBook.getContainer()));
            
            return new AppContainer([authorHeader].concat(audioBookElements)).element;
        }

        return displayNotFound();
    }
}