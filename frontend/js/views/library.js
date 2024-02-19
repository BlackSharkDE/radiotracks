/**
 * Bibliothek-Seite
 */

class LibraryView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - Bibliothek");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {

        let header = new AppContainerHead("Bibliothek");

        let artists   = new AppContainerItem("res/library/artists.jpg","Künstler","Die besten Musiker",() => { navigateTo(getRouteWithoutParameters(4)); });
        let authors   = new AppContainerItem("res/library/authors.jpg","Autoren","Hörbücher",() => { navigateTo(getRouteWithoutParameters(7)); });
        let channel   = new AppContainerItem("res/library/channels.jpg","Channels","Radiostationen",() => { navigateTo(getRouteWithoutParameters(10)); });
        let playlists = new AppContainerItem("res/library/playlists.jpg","Playlists","Von Radiotracks kuratiert",() => { navigateTo(getRouteWithoutParameters(11)); });
        let podcasts  = new AppContainerItem("res/library/podcasts.jpg","Podcasts","Der sinnvollste Zeitvertreib",() => { navigateTo(getRouteWithoutParameters(13)); });

        return new AppContainer([header,artists,authors,channel,playlists,podcasts],false).element;
    }
}