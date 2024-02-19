/**
 * Abstrakte View-Klasse, auf der alle anderen View-Klassen der SPA aufbauen
 */
class AbstractSPAView {

    /**
     * -- Konstruktor --
     * @param Object Die Parameter aus der URL für die View
     *               - OPTIONAL (eine View muss keine Parameter verarbeiten)
     *               - Käme von der "getParams"-Funktion in "spa.js", die die Parameter in die jeweilige Child-View-Klassen übergibt
     */
    constructor(params = null) {
        this.params = params;
    }

    /**
     * Setzt den Title des Tabs. (void - Funktion)
     * @param string Titel des Tabs
     */
    setTitle(title) {
        document.title = title;
    }

    /**
     * Gibt das HTML für das "app"-Div zurück (also das was die View ausgibt)
     * @return String / HTML-Element => Das HTML der View als String oder als HTML-Element / DOM-Objekt
     */
    async getHtml() {
        return "";
    }

    /**
     * Optionale Methode, die nach "getHtml()" ausgeführt wird. Sie kann alles Mögliche beinhalten. (void - Funktion)
     */
    async afterHtml() {
    }
}