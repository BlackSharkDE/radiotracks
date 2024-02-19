/**
 * Gesamte Logik, die mit dem "Single-Page-Application"-Feel zutun hat
 * 
 * =================================================================================================================================================================
 * Das Skript setzt eine Variable namens "routes" voraus, welche ein Array darstellt.
 * 
 * Dieses enthält alle möglichen Routen, diese bestehen aus:
 * - Einem String "path", nach dem Muster: /routePath/route_Path/:parameterName_1/:parameterName_2 ...
 * - Einer "view"-Klasse (Child-Klasse von "AbstractSPAView"-Klasse), die bei der Route angezeigt werden soll
 *   => Wichtig, dass dies die Klasse und kein Objekt der Klasse ist!
 *
 * Beispiel:
 * const routes = [
 *     //Index-Seite bzw. View
 *     { path: "/", view: DashboardViewClass },
 *
 *     //Normale bzw. nicht sehr tiefe Routen
 *     { path: "/posts", view: ViewForPosts },
 *     { path: "/settings", view: SettingsView },
 *
 *     //Beliebig tiefe Routen sind möglich
 *     { path: "/library/books/science", view: ViewScienceBooks },
 * 
 *     //Routen mit beliebigen Parametern
 *     { path: "/post/:name/:author/:published", view: PostView },
 *     { path: "library/book/:id", view: ViewABook },
 * 
 *     //Die letzte View wird immer ausgegeben, wenn die angesurfte Route nicht zugeordnet werden kann
 *     { path: "/404", view: NotFound }
 * ]
 * 
 * =================================================================================================================================================================
 * 
 * Zudem benötigt das Skript ein <div> mit der id "app": <div id="app"></div>
 * Dieses wird benötigt, um den Inhalt der einzelnen Views (HTML) anzuzeigen.
 * 
 * =================================================================================================================================================================
 * Interne Verlinkungen
 * 
 * Um innerhalb der SPA die Views zu wechseln, entweder die "navigateTo"-Funktion benutzen (z.B. über eigene "onClick"-Events) oder Links mit 
 * dem "data-link"-Attribut benutzen: <a href="/posts" data-link>Zu den Posts navigieren</a>
 */

//==================================================================================================================================================================
//-- Router --

/**
 * Konvertiert einen "path" einer Route (siehe "routes"-Array) in einen Regex-Ausdruck
 * @param string  "path"-Attribut einer Route
 * @return RegExp Ein Regex-Ausdruck
 */
const spaRouter_pathToRegex = path => new RegExp(
    "^"                          //Anfang des Strings
    + path.replace(/\//g, "\\/") //Jeden "/" mit dem Regex-Äquivalent ersetzen
    .replace(/:\w+/g, "(.+)")    //Jeden ":parameterName" mit einer Regex-Capture-Group ersetzen
    + "$"                        //Ende des Strings
);

/**
 * Extrahiert die Parameternamen und Werte aus der URL
 * @param RegexMatch Ein Regex-Match-Objekt
 * @return Object    Ein Objekt mit den ":parameterName"-Strings als Keys und den enstprechenden Werten aus der URL als Values
 */
const spaRouter_getParams = match => {

    //Parmater-Werte als Array
    //- Vom "result"-Array von "match" ab Index 1 befinden sich die Parameterwerte
    //- Index 0 ist die komplette Route selbst (also die angesurfte URL mit den Parametern)
    const values = match.result.slice(1);

    //Parameter-Namen als Array
    //- Nehme die Route selbst (nicht die URL) und finde alle ":parameterName"-Strings => Array.from(), viele Arrays
    //- Mappe jeden Index 1 (der Parametername) von jedem Array in ein neues Array => .map()
    const keys = Array.from(match.route.path.matchAll(/:(\w+)/g)).map(result => result[1]);

    return Object.fromEntries(keys.map((key, indexOfKey) => {
        return [key, values[indexOfKey]];
    }));
};

//Sucht die entsprechende View heraus und zeigt diese an (benötigt "routes"-Array). (void - Funktion)
const spaRouter = async () => {

    //console.log("(spaRouter) Current location: " + location.pathname); //DEBUG

    //Array "potentialMatches", enthält Objekte bestehend aus:
    //- Dem Pfad einer Route
    //- Resultat von "match(spaRouter_pathToRegex())", also null ODER ein Array
    const potentialMatches = routes.map(route => {
        return {
            route: route,
            result: location.pathname.match(spaRouter_pathToRegex(baseURLNoEndSlash + route.path))
        };
    });

    //Das Objekt in "potentialMatches" finden, welches im Attribut "result" ein Array hat bzw. nicht null ist
    let match = potentialMatches.find(potentialMatch => potentialMatch.result !== null);

    //Wenn keine Route passt, die letzte Seite als Match einsetzen
    if(!match) {
        match = {
            route: routes[routes.length - 1],
            result: [location.pathname]
        };
    }
    
    //Neues View-Objekt der Route erstellen (Konstruktor der Klasse mit den Parametern in der URL aufrufen)
    const view = new match.route.view(spaRouter_getParams(match));

    //-- HTML-Inhalt der View in das <div> mit der id "app" einspeisen --
    let app = document.querySelector("#app"); //<div> mit der ID "app" finden

    //Sollte "standardAppContent" angegeben worden sein
    if(typeof standardAppContent !== "undefined") {

        //Je nachdem, wie der Inhalt von "standardAppContent" ist
        if(typeof standardAppContent === 'string') {
            //"standardAppContent" ist HTML als String (überschreibt alten Content)
            app.innerHTML = standardAppContent;
        } else {
            //Aktuellen Content entfernen
            app.innerHTML = "";

            //"standardAppContent" ist ist ein HTML-Element / DOM-Objekt
            app.appendChild(standardAppContent);
        }
    }

    //Neuen Content (die View) laden
    let newAppContent = await view.getHtml();

    //Je nachdem, wie der Inhalt der View übergeben wurde
    if(typeof newAppContent === 'string') {
        //Neuer Content ist HTML als String (überschreibt alten Content)
        app.innerHTML = newAppContent;
    } else {
        //Aktuellen Content entfernen
        app.innerHTML = "";

        //Neuer Content ist ein HTML-Element / DOM-Objekt
        app.appendChild(newAppContent);
    }

    //Optionale Methode "afterHtml" ausführen
    await view.afterHtml();
}

//==================================================================================================================================================================
//-- Events --

//Wenn man im Browser auf die Vor- und Zurück-Taste geht
window.addEventListener("popstate", spaRouter);

//Wenn das HTML-Dokument komplett geparst und alle Skripte gedownloaded und ausgeführt wurden
//=> wartet nicht auf Bilder, Subframes und asynchrone Scripte
document.addEventListener("DOMContentLoaded", () =>  {
    
    //Neuer Event-Listener, wenn man auf einen Link klickt, der das "data-link"-Attribut hat
    document.body.addEventListener("click", e => {
        if(e.target.matches("[data-link]")) {
            //Standardverhalten unterbinden
            e.preventDefault();

            //Eigene Navigationsfunktion benutzen
            navigateTo(e.target.href);
        }
    });

    //Prüfen, ob "routes"-Variable definiert und ein Array ist
    if(typeof routes !== "undefined" && Array.isArray(routes)) {
        //Den SPA-Router ausführen
        spaRouter();
    } else {
        //Fehler in Konsole ausgeben
        console.error("The 'routes' variable is not defined or no array! => Will not run the 'spaRouter' function!");
    }
});

//==================================================================================================================================================================
//-- Weiteres --

//Wert im <base>-Tag, ohne dass es eine komplette (errechnete) URL ist
const baseURL             = document.getElementsByTagName('base')[0].getAttribute("href");
const baseURLNoEndSlash   = baseURL.substring(0,baseURL.length - 1); //Gleich wie "baseURL" aber ohne "/" am Ende
const baseURLNoStartSlash = baseURL.substring(1);                    //Gleich wie "baseURL" aber ohne "/" am Anfang

//Navigiert zu einer URL. (void - Funktion)
const navigateTo = url => {
    //Der Browser-History hinzufügen
    history.pushState(null,null,url);

    //Den SPA-Router ausführen
    spaRouter();
};

/**
 * Zeigt die "Not Found Seite" an. (void - Funktion)
 * Das Benutzen dieser Funktion hat den Vorteil, das die URL erhalten bleibt und trotzdem die 404-Seite angezeigt wird.
 */
async function displayNotFound() {
    return await (new (routes[routes.length - 1].view)()).getHtml();
}

/**
 * Gibt Routen-Pfade aus "routes"-Array ohne Parameter zurück
 * @param Int     Index in "routes"-Array
 * @return String Route ohne URL-Parameter (ohne "/" am Ende)
 */
function getRouteWithoutParameters(routesIndex) {

    //Pfad des Route-Index
    let rp = baseURLNoEndSlash + routes[routesIndex].path;
    
    //Position des letzten Slash ohne Parameter in der Route
    let lastSlashPosition = rp.indexOf("/:");

    //Wenn das letzte Slash ohne Parameter nicht von "baseURL" stammt, hat die Route URL-Parameter
    if(lastSlashPosition > baseURL.lastIndexOf("/")) {
        //Route ohne URL-Parameter
        return rp.substring(0,lastSlashPosition);
    }

    //Die Route (ist sowieso ohne URL-Parameter)
    return rp;
}