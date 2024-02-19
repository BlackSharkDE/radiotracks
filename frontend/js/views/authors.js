/**
 * Authors-Seite
 */

class AuthorsView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - Autoren");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {
        
        //Alle Author-JSON-Objekte von der API abfragen
        var authors = await api.getResult("author/all");

        //Prüfe, ob Antwort nicht leer
        if(Object.keys(authors).length > 0) {
            let containerHead = new AppContainerHead("Alle Autoren");

            //Authors anhand der Namen sortieren
            authors.sort(sortByName);

            //Alle Author-HTML-Elemente
            var authorElements = [];
            authors.forEach(author => {
                let authorObject = new Author(author);
                authorObject.setContainer();
                authorElements.push(authorObject.getContainer());
            });
            
            return new AppContainer([containerHead].concat(authorElements)).element;
        }

        return displayNotFound();
    }
}