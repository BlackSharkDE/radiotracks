/**
 * Die 404 / Not Found-Seite
 */

class NotFoundView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Not found");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {

        //Div für Informationstext
        var errorDiv = Object();
        errorDiv.element = document.createElement("div"); //Für AppContainer die DOM-Elemente im "element"-Attribut speichen

        //Radiotracks-Logo
        var img = document.createElement("img");
        img.src = "res/radiotracks.png";
        img.alt = "radiotracks_logo_not_found";
        img.style.height = "100px";
        img.style.width  = "100px";
        img.style.marginTop = "20px";
        errorDiv.element.appendChild(img);

        //Überschrift
        var h = document.createElement("h1");
        h.innerText = "Seite nicht gefunden";
        errorDiv.element.appendChild(h);

        //Text
        var p = document.createElement("p");
        p.innerText = "Radiotracks kann die angegebene Seite nicht finden.";
        errorDiv.element.appendChild(p);

        return new AppContainer([errorDiv],false).element;
    }
}