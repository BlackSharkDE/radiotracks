/**
 * Suchen-Seite
 */

class SearchView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - Suche");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {

        //Inhalt der Suchen-Seite
        let searchContainerList = [];

        //-- Container mit dem Suchen-Element --
        let searchDiv = Object();
        searchDiv.element = document.createElement("div");
        searchDiv.element.style.width           = "100%";
        searchDiv.element.style.textAlign       = "left";
        searchDiv.element.style.height          = "40px";
        searchDiv.element.style.backgroundColor = "#ffffff";
        searchDiv.element.style.borderRadius    = "30px";
        searchDiv.element.style.marginBottom    = "25px";

        //Suche-Symbol
        let searchSymbole = document.createElement("i");
        searchSymbole.classList.add("fa","fa-search");
        searchSymbole.style.fontSize   = "30px";
        searchSymbole.style.float      = "left";
        searchSymbole.style.color      = "#000000";
        searchSymbole.style.marginLeft = "15px";
        searchSymbole.style.marginTop  = "5px";
        searchDiv.element.appendChild(searchSymbole);
        
        //Suche-Input
        let searchInput = document.createElement("input");
        searchInput.id = "searchInput";
        searchInput.placeholder = "Was möchtest du hören?";
        searchInput.style.backgroundColor = "#ffffff";
        searchInput.style.color           = "#000000";
        searchInput.style.marginLeft      = "8px";
        searchInput.style.height          = "40px";
        searchInput.style.width           = "calc(100% - 70px)";
        searchInput.style.outline         = "none";
        searchInput.style.border          = "none";
        searchInput.style.fontSize        = "18px";
        searchInput.style.fontFamily      = "inherit"; //Schriftart explizit erben
        searchInput.style.float           = "left";
        searchInput.style.padding         = "0"; //iOS-Standard-Padding entfernen
        searchDiv.element.appendChild(searchInput);

        //Erst die Suche starten, wenn fertig mit tippen
        let typingTimer;
        let doneTypingInterval = 600;
        searchInput.onkeyup = () => {
            //-- Countdown starten --
            clearTimeout(typingTimer);
            typingTimer = setTimeout(() => {
                //-- Wenn etwas in das Suchfeld eingegeben wird, die View neu laden --
                if(searchInput.value.length > 0) {
                    navigateTo(getRouteWithoutParameters(1) + "/" + encodeURIComponent(searchInput.value));
                } else {
                    navigateTo(getRouteWithoutParameters(1));
                }
            },doneTypingInterval);
        }
        searchInput.onkeydown = () => {
            //-- Countdown entfernen --
            clearTimeout(typingTimer);
        }

        let searchContainer = new AppContainer([searchDiv]);
        searchContainerList.push(searchContainer);

        //-- Wenn etwas gesucht wurde --
        if(typeof this.params.searchTerm !== 'undefined') {

            //Wenn in der URL ein Term steht, diesen in das Suchfeld eintragen
            searchInput.value = decodeURIComponent(this.params.searchTerm);

            //Suchergebnis von der API abfragen
            var searchResult = await api.getResult("search/" + this.params.searchTerm);

            /**
             * Erstellt ein Suchergebis-Container und hängt es der "searchContainerList" an (void - Funktion)
             * @param string Was im Suchergebis-Head stehen soll
             * @param string Sektion in "searchResult"-JSON
             * @param Class  Klassen-Referenz für Objekte, die im Suchergebis enthalten sind
             */
            function addResultToList(headText,apiJsonSection,classRef) {
                let resultHead = new AppContainerHead(headText);
                let resultContent = Array.from(searchResult[apiJsonSection], item => {
                    let itemObject = new classRef(item);
                    itemObject.setContainer();
                    return itemObject.getContainer();
                });
                resultContent = new AppContainer([resultHead].concat(resultContent));
                searchContainerList.push(resultContent);
            }

            //Wenn API-Rückgabe gültig ist
            if(Object.keys(searchResult).length > 0) {
                
                //-- Artists --
                if(searchResult["artists"].length > 0) {
                    addResultToList("Künstler","artists",Artist);
                }

                //-- Albums --
                if(searchResult["albums"].length > 0) {
                    addResultToList("Alben","albums",Album);
                }

                //-- Authors --
                if(searchResult["authors"].length > 0) {
                    addResultToList("Autoren","authors",Author);
                }

                //-- AudioBooks --
                if(searchResult["audiobooks"].length > 0) {
                    addResultToList("Hörbücher","audiobooks",AudioBook);
                }

                //-- Channels --
                if(searchResult["channels"].length > 0) {
                    addResultToList("Channels","channels",Channel);
                }

                //-- Playlists --
                if(searchResult["curatedplaylists"].length > 0) {
                    addResultToList("Channels","curatedplaylists",Playlist);
                }

                //-- Podcasts --
                if(searchResult["podcasts"].length > 0) {
                    addResultToList("Podcasts","podcasts",Podcast);
                }

                //-- Tracks --
                if(searchResult["tracks"].length > 0) {

                    //Neuen Head erstellen
                    let resultHead = new AppContainerHead("Tracks");

                    //Track-Array
                    let tracks = [];

                    //Tracks erstellen
                    searchResult["tracks"].forEach(track => {

                        //Wohin navigiert werden soll
                        let navigateRoute = "";

                        //Je nachdem, ob der Track ein Album-Track oder eine Podcast-Episode ist
                        if(track.hasOwnProperty("albumId")) {
                            navigateRoute = "album/" + track["albumId"];
                        } else if(track.hasOwnProperty("podcastId")) {
                            navigateRoute = "podcast/" + track["podcastId"];
                        }

                        //Neuen Track hinzufügen
                        tracks.push(new Track(track,track["artist"],track["album"],getMediaPathUrl(track["cover"]),() => { navigateTo(navigateRoute); }));
                    });

                    //Tracktable
                    let trackTable = new AppTracktable(tracks,true,true);

                    //Head und Tracktable
                    searchContainerList.push(new AppContainer([resultHead,trackTable]));
                }
            }
        }

        return new AppContainer(searchContainerList,false).element;
    }

    //Überschreibe "afterHtml"-Methode
    afterHtml() {

        //Refokus vom Suchen-Input
        //=> funktioniert auf Mobile nur, wenn die Seite zum ersten Mal geladen wird
        let s = document.getElementById("searchInput");
        s.onclick = () => {
            s.focus();
        };

        //Automatisch auf Input klicken
        s.click();
    }
}