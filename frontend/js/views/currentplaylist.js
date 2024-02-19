class CurrentPlaylistView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - Aktuelle Playlist");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {

        //Button zum leeren der Playlist
        var trashButton = document.createElement("button");
        trashButton.innerHTML = '<i class="fa fa-trash">';
        trashButton.onclick = () => { webplayer.deletePlaylist(); };

        //Head
        var containerHead = new AppContainerHead("Aktuelle Playlist",trashButton);

        //Tracktable
        var trackTable = new AppTracktable([],true,true);

        if(!(webplayer.currentObject instanceof Channel)) {
            trackTable = new AppTracktable(webplayer.playlist,true,true,true,true);
        }

        webplayer.currentTracktable = trackTable;
        webplayer.showTracktableEqualiser();
        
        //Header und Tracktable in einen Container packen und diesen ausgeben
        return new AppContainer([containerHead,trackTable],false).element;
    }

    //Überschreibe "afterHtml"-Methode
    async afterHtml() {

        //Wenn ein Tracktable definiert ist
        if(webplayer.currentTracktable !== null) {
            webplayer.focusTrack();
        }
    }
}