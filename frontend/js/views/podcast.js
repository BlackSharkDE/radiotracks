/**
 * Podcast-Seite
 */

class PodcastView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - Podcast");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {

        //Podcast von der API abfragen
        var podcast = await api.getResult("podcast/id/" + this.params.id);

        //Prüfe, ob Podcast gefunden wurde
        if(Object.keys(podcast).length > 0) {
            podcast = new Podcast(podcast);

            //Titel überschreiben
            this.setTitle("Radiotracks - " + podcast.name);

            //Podcast-Header
            var podcastHeader = new AppContainerHeader(
                podcast.cover,
                "Podcast",
                podcast.name,
                [
                    "Episoden: " + podcast.episodeCount
                ],
                () => { webplayer.play(podcast,true); }
            );

            //Beschreibung des Podcast
            var infoContainer = new AppContainerInfo("Beschreibung",podcast.description);

            //Alle Episoden des Podcast abfragen
            var podcastEpisodes = await api.getResult("podcast/episodes/id/" + this.params.id);
            podcast.setEpisodes(podcastEpisodes);

            //Tracktable
            var trackTable = new AppTracktable(podcast.tracks,false,false,false);

            //Header, Beschreibung und Tracktable in einen Container packen und diesen ausgeben
            return new AppContainer([podcastHeader,infoContainer,trackTable],false).element;
        }

        return displayNotFound();
    }
}