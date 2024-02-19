/**
 * Artists-Seite
 */

class ArtistsView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - Künstler");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {

        //Alle Artist-JSON-Objekte von der API abfragen
        var artists = await api.getResult("artist/all");

        //Prüfe, ob Antwort nicht leer
        if(Object.keys(artists).length > 0) {
            let containerHead = new AppContainerHead("Alle Künstler");

            //Artists anhand der Namen sortieren
            artists.sort(sortByName);

            //Alle Artist-HTML-Elemente
            var artistElements = [];
            artists.forEach(artist => {
                let artistObject = new Artist(artist);
                artistObject.setContainer();
                artistElements.push(artistObject.getContainer());
            });

            return new AppContainer([containerHead].concat(artistElements)).element;
        }

        return displayNotFound();
    }
}