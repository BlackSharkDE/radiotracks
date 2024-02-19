/**
 * Index-Seite
 */

class IndexView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - Start");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {

        //Enthält Container, die wiederum Artists etc. enthalten
        var indexContainerList = []

        //Abfragen der Spotlights
        var spotlights = await api.getResult("spotlights");

        /**
         * Erstellt ein Spotlight und hängt es der "indexContainerList" an (void - Funktion)
         * @param string Was im Spotlight-Head stehen soll
         * @param string Sektion in "spotlights"-JSON
         * @param Class  Klassen-Referenz für Objekte, die im Spotlight enthalten sind
         */
        function addSpotlightToList(headText,apiJsonSection,classRef) {
            let spotlightHead = new AppContainerHead(headText);
            let spotlightContent = Array.from(spotlights[apiJsonSection], item => {
                let itemObject = new classRef(item);
                itemObject.setContainer();
                return itemObject.getContainer();
            });
            spotlightContent = new AppContainer([spotlightHead].concat(spotlightContent));
            indexContainerList.push(spotlightContent);
        }

        //Wenn API-Rückgabe gültig ist
        if(Object.keys(spotlights).length > 0) {

            //-- Artists --
            if(spotlights["artists"].length > 0) {
                addSpotlightToList("Spotlight - Künstler","artists",Artist);
            }

            //-- Authors --
            if(spotlights["authors"].length > 0) {
                addSpotlightToList("Spotlight - Autoren","authors",Author);
            }

            //-- Channels --
            if(spotlights["channels"].length > 0) {
                addSpotlightToList("Spotlight - Channels","channels",Channel);
            }

            //-- Playlists --
            if(spotlights["playlists"].length > 0) {
                addSpotlightToList("Spotlight - Playlists","playlists",Playlist);
            }

            //-- Podcast --
            if(spotlights["podcasts"].length > 0) {
                addSpotlightToList("Spotlight - Podcasts","podcasts",Podcast);
            }

            //Zufällige Anordnung der Spotlights
            indexContainerList.sort(() => Math.random() - 0.5);

            return new AppContainer(indexContainerList,false).element;
        }

        return displayNotFound();
    }
}