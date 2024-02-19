/**
 * Channels-Seite
 */

class ChannelsView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - Channels");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {

        //Alle Channel-JSON-Objekte von der API abfragen
        var channels = await api.getResult("channel/all");

        //Prüfe, ob Antwort nicht leer
        if(Object.keys(channels).length > 0) {
            let containerHead = new AppContainerHead("Alle Channels");

            //Channel anhand der Namen sortieren
            channels.sort(sortByName);

            //Alle Channel-HTML-Elemente
            var channelElements = [];
            channels.forEach(channel => {
                let channelObject = new Channel(channel);
                channelObject.setContainer();
                channelElements.push(channelObject.getContainer());
            });

            return new AppContainer([containerHead].concat(channelElements)).element;
        }

        return displayNotFound();
    }
}