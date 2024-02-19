/**
 * Alles für die Netzwerkkommunikation
 */

//==================================================================================================================================================================
//-- Einstellungen --

//URL in den Ordner, in dem der "media-Ordner liegt" -> mit "/" am Ende!
const mediaUrl = "http://192.168.178.18/Radiotracks-4/";

//API-Einstellungen
const apiUrl   = "http://192.168.178.18"; //URL zur API -> ohne "/" am Ende!
const apiPort  = "8080"; //Port der API

//HTTP-Basic-Auth (OPTIONAL)
const HTTPUser = ""; //HTTP-Basic-Auth - User
const HTTPPass = ""; //HTTP-Basic-Auth - Passwort für User

//==================================================================================================================================================================
//-- Alles für die API-Verbindung --

class Api {

    /**
     * Gibt ein Promise für den API-Request zurück
     * @param String   Komplette URL, die aufgerufen werden soll
     * @return Promise Ein Promise, welches den API-Request ausführt
     */
    getApiRequest(completeUrl) {

        return new Promise((resolve, reject) => {

            //Request erstellen
            let xhr      = new XMLHttpRequest();
            xhr.timeout  = 15000; //15 Sekunden bis Timeout
            xhr.open("GET",completeUrl,true); //Immer GET, die URL, immer asynchron

            //Prüfe Status der Verbindung
            xhr.onload = () => {
                if(xhr.status >= 200 && xhr.status < 300) {
                    //Verbindung OK
                    resolve(xhr.response);
                } else {
                    //Verbindung nicht OK
                    reject({
                        status: xhr.status,
                        statusText: xhr.statusText
                    });
                }
            };

            //Wenn die Verbindung einen Timeout hat
            xhr.ontimeout = () => {
                reject({
                    status: 408,
                    statusText: "The request timed out!"
                });
            }

            //Wenn die Verbindung fehlschlägt
            xhr.onerror = () => {
                reject({
                    status: xhr.status,
                    statusText: xhr.statusText
                });
            }

            xhr.send(null);
        });
    }

    /**
     * Die API abfragen (asynchron)
     * @param String URL innerhalb API (ohne Protokoll und Host), z.B.: "album/id/1234567890" 
     * @return JSON  Ein JSON-Objekt (leeres Objekt wenn nicht gefunden oder Probleme bei Verbindung)
     */
    async getResult(apiPath) {

        //Komplette API-URL erstellen
        const completeUrl = apiUrl + ":" + apiPort + "/" + apiPath;
        //console.log(completeUrl); //DEBUG

        //Das Ergebis der API-Anfrage
        let apiResult = "{}";

        //Versuche API abzufragen
        try {
            apiResult = await this.getApiRequest(completeUrl);
        } catch(e) {
            console.error("An error occured while connecting to the API! Status: " + e.status + " | Text: " + e.statusText);
            showNotification("Konnte keine Verbindung zum Server herstellen!",0,true);
        }

        //JSON parsen
        apiResult = JSON.parse(apiResult);
        //console.log(apiResult); //DEBUG

        return apiResult;
    }
}

//Statische Variable, die die API enthält
const api = new Api();

//==================================================================================================================================================================
//-- Anderweitige Verbindung --

/**
 * Bettet ggf. (sofern "HTTPUser" und "HTTPPass" angegeben wurden) HTTP-Anmeldedaten in die übergebene URL ein
 * @param string  URL, in die ggf. eingebettet werden soll
 * @return string Gleiche URL mit "HTTPUser" und "HTTPPass" in URL eingebettet
 */
function embedCredentials(urlToResource) {
    let embeddedCredentials = urlToResource;

    //Sofern HTTP-Anmeldedaten angegeben wurde, diese in die URL einbetten
    if(HTTPUser.length > 0 && HTTPPass.length > 0) {
        embeddedCredentials = urlToResource.replace("//","//" + HTTPUser + ":" + HTTPPass + "@");
    }

    return embeddedCredentials;
}

/**
 * Definiert ein GET-"fetch"-Promise mitsamt HTTP-Auth-Header, sofern Anmeldedaten angegeben wurden
 * 
 * Hinweise:
 * => Bei CORS-Ressourcen funktioniert dies nicht
 * => Wenn der Fetch zu einer bereits geladenen Ressource geht, sollte der Cache die Datei liefern (es wird dann kein Request gemacht)
 * 
 * @param string   Url, die gefetcht werden soll
 * @return Promise Ein Fetch-Promise, welches sich in ein "Blob"-Objekt auflöst (entweder die angeforderte Ressource oder leerer Blob mit Notification-Anzeige)
 */
function fetchWithAuthentication(urlToFetch) {

    //Headers für fetch
    let headers = new Headers();

    //Sollten HTTP-Anmeldedaten angeben worden sein, diese den Headern hinzufügen
    if(HTTPUser.length > 0 && HTTPPass.length > 0) {
        headers.set('Authorization',`Basic ${btoa(HTTPUser + ":" + HTTPPass)}`);
    }

    //console.log("Fetching URL (fetchWithAuthentication): " + urlToFetch); //DEBUG

    return(
        fetch(
            urlToFetch,
            {
                method : 'GET',
                headers: headers
            }
        )
        .then((response) => {
            if(response.ok) {
                //-- Alles ok, Ressource wurde geladen --
                return response.blob()
            }

            //-- Nicht gefunden / CORS --
            throw new Error("An error occured while fetching! Status: " + response.status + " | Text: " + response.statusText)
        })
        .catch(anyError => {
            console.error(anyError);
            showNotification("Fehler beim Laden einer Ressource!",0,true);
            return new Blob();
        })
    );
}