/**
 * Podcasts-Seite
 */

class PodcastsView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - Podcasts");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {

        //Alle Podcast-JSON-Objekte von der API abfragen
        var podcasts = await api.getResult("podcast/all");

        //Prüfe, ob Antwort nicht leer
        if(Object.keys(podcasts).length > 0) {
            let containerHead = new AppContainerHead("Alle Podcasts");

            //Podcasts anhand der Namen sortieren
            podcasts.sort(sortByName);

            //Alle Podcast-HTML-Elemente
            var podcastElements = [];
            podcasts.forEach(podcast => {
                let podcastObject = new Podcast(podcast);
                podcastObject.setContainer();
                podcastElements.push(podcastObject.getContainer());
            });

            return new AppContainer([containerHead].concat(podcastElements)).element;
        }

        return displayNotFound();
    }
}