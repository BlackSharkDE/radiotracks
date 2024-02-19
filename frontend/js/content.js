/**
 * Inhalte im <app>-Div (HTML-Elemente)
 */

//==================================================================================================================================================================
//-- Items der Container --

//Items in den Containern
class AppContainerItem {

    /**
     * -- Konstruktor --
     * @param String   Bild-URL
     * @param String   Was in dem ersten Text-Abteil stehen soll
     * @param String   Was in dem zweiten Text-Abteil stehen soll
     * @param Function Funktion / Funktionspointer, was beim "onClick"-Event ausgeführt werden soll (OPTIONAL)
     */
    constructor(imageUrl,textForOne,textForTwo,onclickFunction = null) {
        //Äußeres <div>
        this.element = document.createElement("div");
        this.element.classList.add("app__container__item");
        this.element.onclick = onclickFunction;

        //-- <div> für Image --
        var imageDiv = document.createElement("div");
        imageDiv.classList.add("app__container__item__imagewrapper");

        //Image
        var image = document.createElement("img");
        image.src = "res/loading.svg";
        fetchWithAuthentication(imageUrl).then((blob) => { displayImage(blob,image); }); //Asynchron Bild laden und anzeigen
        image.alt = imageUrl;
        image.ondragstart = () => { return false; }; //Bilder-Drag unterbinden

        imageDiv.appendChild(image);

        //-- <div> für Text --
        var textDiv = document.createElement("div");
        textDiv.classList.add("app__container__item__text");
        
        var textOne = document.createElement("p");
        textOne.classList.add("app__container__item__text__one");
        textOne.innerText = textForOne;

        var textTwo = document.createElement("p");
        textTwo.classList.add("app__container__item__text__two");
        textTwo.innerText = textForTwo;

        textDiv.appendChild(textOne);
        textDiv.appendChild(textTwo);

        //Dem äußeren <div> hinzufügen
        this.element.appendChild(imageDiv);
        this.element.appendChild(textDiv);
    }
}

//==================================================================================================================================================================
//-- Container --

//Überschrift im Container
class AppContainerHead {
    
    /**
     * -- Konstruktor --
     * @param String Was in der Überschrift stehen soll
     * @param Button Ein HTML/DOM-Button, der auf der rechten Seite des Head angezeigt werden soll (OPTIONAL)
     */
    constructor(headingText,rightButton = null) {
        //Äußeres <div>
        this.element = document.createElement("div");
        this.element.classList.add("app__container__head");

        //<p> innerhalb <div>
        var p = document.createElement("p");
        p.innerText = headingText;
        this.element.appendChild(p);

        //Wenn ein <button> angegeben wurde
        if(rightButton !== null) {
            this.element.appendChild(rightButton);
        }
    }
}

//Container-Header
class AppContainerHeader {

    /**
     * -- Konstruktor --
     * @param String   URL des Bildes, welches angezeigt werden soll
     * @param String   Welcher Typ angezeigt werden soll ("Album", "Künstler", etc.)
     * @param String   Welcher Name angezeigt werden soll (der eines Albums, Künstlers, etc.)
     * @param Array    Was in der Beschreibung stehen soll (String-Array ; kann HTML beinhalten ; werden mittels Bullet-Points aneinandergereiht)
     * @param Function Eine Funktion, die ausgeführt werden soll, wenn auf das Bild geklickt wird
     */
    constructor(imageUrl,typeText,nameText,descriptionArray,imageOnClickFunction) {
        //Äußeres <div>
        this.element = document.createElement("div");
        this.element.classList.add("app__container__header");

        //-- Image <div> --
        var imageDiv = document.createElement("div");
        imageDiv.classList.add("app__container__header__image");
        imageDiv.onclick = imageOnClickFunction;
        
        //Bild
        var img = document.createElement("img");
        img.src = "res/loading.svg";
        img.alt = imageUrl;
        img.ondragstart = () => { return false; }; //Bilder-Drag unterbinden

        //Asynchron das Bild downloaden und die Hintergrundfarbe im "element"-Div ändern
        fetchWithAuthentication(imageUrl)
        .then((blob) => {
            setAverageColor(blob,this.element);
            displayImage(blob,img);
        });

        imageDiv.appendChild(img);

        this.element.appendChild(imageDiv);

        //-- Text <div> --
        var textDiv = document.createElement("div");
        textDiv.classList.add("app__container__header__text");

        //Type
        var type = document.createElement("p");
        type.classList.add("app__container__header__text__type");
        type.innerText = typeText.toUpperCase();
        textDiv.appendChild(type);

        //Name
        var name = document.createElement("p");
        name.classList.add("app__container__header__text__name");
        name.innerText = nameText;
        textDiv.appendChild(name);

        //Description
        var description = document.createElement("p");
        description.classList.add("app__container__header__text__description");
        descriptionArray.forEach((descriptionItem, index, arr) => {
            description.innerHTML += descriptionItem;

            //Nur einen Bullet-Point hinzufügen, wenn noch nicht letztes Item
            if(index < arr.length - 1) {
                description.innerHTML += " &bull; "
            }
        });
        
        textDiv.appendChild(description);

        this.element.appendChild(textDiv);
    }
}

//Cointainer für extra Informationen
class AppContainerInfo {

    /**
     * -- Konstruktor --
     * @param string Überschrift
     * @param string Information
     */
    constructor(heading,text) {
        //Äußeres <div>
        this.element = document.createElement("div");
        this.element.classList.add("app__container__info");

        //Überschrift (<h2>)
        var infoHeading = document.createElement("h2");
        infoHeading.innerText = heading;
        this.element.appendChild(infoHeading);

        //Text (<p>)
        var infoText = document.createElement("p");
        infoText.innerText = text;
        this.element.appendChild(infoText);
    }
}

//Container selbst
class AppContainer {
    
    /**
     * -- Konstruktor --
     * @param array Array mit Objekten, die im Container angezeigt werden können (besitzen ".element"-Attribut) / leeres Array
     * @param bool  Ob der Container eine Border am unteren Ende haben soll (OPTIONAL)
     */
    constructor(containerItems, withBorder = true) {
        //Äußeres <div>
        this.element = document.createElement("div");
        
        //Border setzen
        if(withBorder === true) {
            this.element.classList.add("app__container_border");
        } else {
            this.element.classList.add("app__container_borderless");
        }

        //Dem äußeren <div> das HTML der "containerItems" hinzufügen
        containerItems.forEach(item => this.element.appendChild(item.element));
    }
}

//==================================================================================================================================================================
//-- Tracktable --

class AppTracktable {

    /**
     * -- Konstruktor --
     * @param array Array mit "Track"-Objekten
     * @param bool  Ob die Cover-Spalte angezeigt werden soll
     * @param bool  Ob die Album-Name-Spalte angezeigt werden soll
     * @param bool  Ob der Artist-Name in der Breite begrenzt sein soll -> ermöglicht bei Deaktivierung Beschreibungen (OPTIONAL)
     * @param bool  Ob bei den onClick-Events der jeweilige Track abgespielt werden soll, statt ihn zur aktuellen Playlist hinzuzufügen (OPTIONAL)
     */
    constructor(trackArray,showCoverColumn,showAlbumColumn,limitArtistName = true,playInsteadOfAdd = false) {

        //Grundtabelle <table>
        this.element = document.createElement("table");
        this.element.classList.add("app__container__tracktable");

        //<colgroup>-Element
        var colgroup = document.createElement("colgroup");
        
        //Styles für <col>-Elemente
        var colgroupStyles = ["width: 50px;","width: 40px;","width: 45%;","width: 40%;","width: 90px;"]; //Wenn Album-Spalte angezeigt wird
        if(!showAlbumColumn) {
            //Wenn Album-Spalte nicht angezeigt wird
            colgroupStyles = ["width: 50px;","width: 40px;","width: auto;","width: 90px;"];
        }
        if(!showCoverColumn) {
            //Wenn Cover-Spalte nicht angezeigt werden soll
            colgroupStyles.splice(1,1); //Entferne Element-Index 1, 1 mal
        }

        //<colgroup> mit <col>-Elementen füllen
        colgroupStyles.forEach(styleEntry => {
            var col = document.createElement("col");
            col.span = 1;
            col.style = styleEntry;

            colgroup.appendChild(col);
        });

        this.element.appendChild(colgroup);

        //<tbody>-Element
        var tableBody = document.createElement("tbody");

        /**
         * Gibt ein passendes <tr>-Element zurück
         * @param bool          Ob diese Tabellenreihe hoverbar ist (OPTIONAL)
         * @return HTML-Element Das <tr>-Element
         */
        function getTableRow(hoverable = true) {
            let tr = document.createElement("tr");
            if(hoverable) {
                tr.classList.add("trhover")
            }
            return tr;
        }

        //Alle möglichen Styles für <th>- und <td>-Elemente
        var tableStyles = ["app__container__tracktable__songnumber","app__container__tracktable__cover","app__container__tracktable__title","app__container__tracktable__album"];

        //Überschrift bauen
        var thRow = getTableRow(false);
        for(let i = 0; i < 5; i++) {
            //<th>-Element
            let th = document.createElement("th");
            
            //Je nachdem, welche Überschrift dran ist
            if(i === 0) {
                th.classList.add(tableStyles[0]);
                th.innerText = "#";
            } else if(i === 1) {
                if(showCoverColumn) {
                    th.innerHTML = "&nbsp;";
                } else {
                    continue;
                }
            } else if(i === 2) {
                th.classList.add(tableStyles[2]);
                th.innerText = "Titel";
            } else if(i === 3) {
                if(showAlbumColumn) {
                    th.classList.add(tableStyles[3]);
                    th.innerText = "Album";
                } else {
                    continue;
                }
            } else if(i === 4) {
                th.innerHTML = '<i class="fa fa-clock-o fa-2x"></i>';
            }
            thRow.appendChild(th);
        }
        tableBody.appendChild(thRow);

        //Track-Reihen bauen
        trackArray.forEach((track,trackIndex) => {
            //<tr>-Element
            let tr = document.createElement("tr");
            tr.classList.add("trhover");

            for(let i = 0; i < 5; i++) {
                //<td>-Element
                let td = document.createElement("td");
                
                //Je nachdem, welcher Inhalt dran ist
                if(i === 0) {
                    td.classList.add(tableStyles[0]);
                    td.innerText = trackIndex + 1;
                } else if(i === 1) {
                    if(showCoverColumn) {
                        td.classList.add(tableStyles[1]);
                        
                        //Album-Cover einstellen
                        let img = document.createElement("img");
                        img.src = "res/loading.svg";
                        fetchWithAuthentication(track.cover).then((blob) => { displayImage(blob,img); }); //Asynchron Cover laden und anzeigen
                        img.alt = track.album;

                        td.appendChild(img);
                    } else {
                        continue;
                    }
                } else if(i === 2) {
                    td.classList.add(tableStyles[2]);

                    //-- Beide <p>-Tags erstellen --
                    let pOne = document.createElement("p");
                    pOne.classList.add("app__container__tracktable__title__name");
                    pOne.innerText = track.title;
                    td.appendChild(pOne);

                    let pTwo = document.createElement("p");
                    pTwo.classList.add("app__container__tracktable__title__artist");
                    pTwo.innerText = track.artist;
                    if(!limitArtistName) {
                        pTwo.style.whiteSpace = "normal";
                    }
                    td.appendChild(pTwo);
                } else if(i === 3) {
                    if(showAlbumColumn) {
                        td.classList.add(tableStyles[3]);
                        td.innerText = track.album;
                    } else {
                        continue;
                    }
                } else if(i === 4) {
                    td.innerText = getDurationFormat(track.duration);
                }
                tr.appendChild(td);
            }

            if(playInsteadOfAdd) {
                tr.onclick = () => { webplayer.setupTrack(trackIndex); };
            } else {
                tr.onclick = () => { webplayer.addTrackToPlaylist(track); };
            }
            
            tableBody.appendChild(tr);
        });
        
        this.element.appendChild(tableBody);
    }

    /**
     * Setzt Zeilen-Nummer in einer Tabellenzeile anstatt des Equaliser-GIF. (void - Funktion)
     * @param int Zeilenindex (Zeile 1 = 0)
     */
    unsetPlayingGif(rowIndex) {
        let tableBody = this.element.tBodies[0];
        let row = tableBody.childNodes[rowIndex + 1]; //+1, weil 0 der Table-Head ist
        if(row !== undefined) {
            row.childNodes[0].innerHTML = rowIndex + 1;
        }
    }

    /**
     * Setzt das Equaliser-GIF in eine Tabellenzeile anstatt der Zeilen-Nummer. (void - Funktion)
     * @param int Zeilenindex (Zeile 1 = 0)
     */
    setPlayingGif(rowIndex) {
        let tableBody = this.element.tBodies[0];
        let row = tableBody.childNodes[rowIndex + 1]; //+1, weil 0 der Table-Head ist
        if(row !== undefined) {
            row.childNodes[0].innerHTML = '<img src="res/equaliser.gif">';
        }
    }

    /**
     * Fokussiert eine Zeile in der Tabelle. (void - Funktion)
     * @param int Zeilenindex (Zeile 1 = 0)
     */
    focusRow(rowIndex) {
        let tableBody = this.element.tBodies[0];
        let row = tableBody.childNodes[rowIndex + 1]; //+1, weil 0 der Table-Head ist
        if(row !== undefined) {
            focusInApp(row);
        }
    }
}