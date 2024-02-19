/**
 * Audio-Visualisierung
 * 
 * Hinweis: Bei quellübergreifenden (cross-origin) Audio-Ressourcen funktioniert dies nicht, da dann der Audio-Processing-Kontext vom Browser automatisch gemuted wird!
 */

//==================================================================================================================================================================
//-- Generelles --

//Damit nicht mehrfach initialisiert wird (muss außerhalb der Klasse sein, damit persistent bzw. statisch)
var VisualizeView_container  = null;
var VisualizeView_visualizer = null;

//Die Rainbow-Intanzen
var canvasRainbowLeft  = null;
var canvasRainbowRight = null;

class VisualizeView extends AbstractSPAView {

    /**
     * -- Konstruktor --
     */
    constructor(params) {
        super(params);
        this.setTitle("Radiotracks - Visualize");
    }

    //Überschreibe "getHtml"-Methode
    async getHtml() {

        //Aktuelles beenden / Zurücksetzen, wenn:
        //- Schon initialisiert
        // UND
        //- Kein Track geladen ODER Webplayer-HTMLMediaElement nicht mehr DASSELBE wie bei Initialisierung
        if((VisualizeView_container !== null && VisualizeView_visualizer !== null)
            && (webplayer.audio.src === "" || VisualizeView_visualizer.source.mediaElement !== webplayer.audio)
        ) {
            //console.log("__DELETE__"); //DEBUG

            //Aktuellen Audio-Processing-Kontext schließen
            VisualizeView_visualizer.context.close();

            //Breche geplanten Draw-Request ab
            VisualizeView_visualizer.cancelAnimationFrame_();

            //Zurücksetzen der Elemente
            VisualizeView_container  = null;
            VisualizeView_visualizer = null;

            //Rainbows beenden
            canvasRainbowLeft.stopRainbow();
            canvasRainbowRight.stopRainbow();
        }

        //Initialisierung / Neuinitialisierung, wenn:
        //- Noch nicht initialisiert
        // UND
        //- Ein Track geladen
        // UND
        //- Aktuell ein Track wiedergegeben wird
        if((VisualizeView_container === null && VisualizeView_visualizer === null) && webplayer.audio.src !== "" && webplayer.audio.paused === false) {
            //console.log("__INITIALIZE__"); //DEBUG

            //Neue Elemente
            VisualizeView_container  = new VisualizerContainer();
            VisualizeView_visualizer = new Visualizer(VisualizeView_container.canvasLeftContext,VisualizeView_container.canvasRightContext);

            //Rainbows starten
            canvasRainbowLeft  = new RainbowObject(VisualizeView_container.canvasLeft,"border-color");
            canvasRainbowLeft.startRainbow();
            canvasRainbowRight = new RainbowObject(VisualizeView_container.canvasRight,"border-color");
            canvasRainbowRight.startRainbow();

            return VisualizeView_container.element;
        }

        //Bereits initialisiertes zurückgeben, wenn:
        //- Schon initialisiert
        // UND
        //- Ein Track geladen UND Webplayer-HTMLMediaElement DASSELBE wie bei Initialisierung ist
        if((VisualizeView_container !== null && VisualizeView_visualizer !== null)
            && (webplayer.audio.src !== "" && VisualizeView_visualizer.source.mediaElement === webplayer.audio)
        ) {
            //console.log("__EXISTS__"); //DEBUG
            return VisualizeView_container.element;
        }

        //-- Wenn alles obige nicht zutrifft, Hinweis ausgeben --
        //console.log("__EMPTY__"); //DEBUG

        //Div für Hinweis
        let empty = document.createElement("div");
        empty.classList.add("app__visualize");
        
        //Der Hinweis
        let hint = document.createElement("p");
        hint.innerHTML = '<i class="fa fa-exclamation-circle"></i>&nbsp;Es spielt gerade kein Audio';
        hint.innerHTML += "<br><br>Ohne geladenen bzw. abspielenden Track<br>kann keine Visualisierung angezeigt werden!";
        hint.classList.add("app__visualize__hint"); //

        empty.append(hint);

        return empty;
    }
}

//==================================================================================================================================================================
//-- Elemente für Darstellung --

class VisualizerContainer {

    /**
     * Ändert die Ränder der Canvas ab. (void - Funktion)
     * @param bool Ob die Ränder jetzt an den Seiten sein sollen
     */
    changeBorders(toSides) {

        if(toSides) {
            //-- Borders an den Seiten --
            this.canvasLeft.style.borderBottomWidth  = "0px";
            this.canvasRight.style.borderBottomWidth = "0px";

            this.canvasLeft.style.borderLeftWidth   = "4px";
            this.canvasRight.style.borderRightWidth = "4px";
        } else {
            //-- Border unten --
            this.canvasLeft.style.borderLeftWidth   = "0px";
            this.canvasRight.style.borderRightWidth = "0px";

            this.canvasLeft.style.borderBottomWidth  = "4px";
            this.canvasRight.style.borderBottomWidth = "4px";
        }
    }

    /**
     * Erstellt und konfiguriert ein Canvas-Element. (void - Funktion)
     * @return Element Ein Canvas-HTML-Element
     */
    createCanvasElement() {

        //Erstelle das Canvas-HTML-Element
        let canvasElement = document.createElement("canvas");
        canvasElement.innerText = "Browser does not support canvas!"; //Platzhalter-Text für fehlende Funktionalität
        canvasElement.classList.add("app__visualize__canvas"); //CSS-Klasse

        //Canvas-Element schon dem "element"-Attribut des Objekts hinzufügen
        this.element.appendChild(canvasElement);

        //Canvas-Element zurückgeben
        return canvasElement;
    }

    /**
     * Erstellt das Cover-Element zwischen den Canvas-Elementen. (void - Funktion)
     */
    createCoverElement() {

        //Cover-Wrapper
        this.bigCover = document.createElement("div");
        this.bigCover.classList.add("app__visualize__bigcover"); //CSS-Klasse

        //Das Cover / Bild
        this.bigCoverImg = document.createElement("img");
        this.bigCover.appendChild(this.bigCoverImg);

        //Automatisch dem "element"-Attribut des Objekts hinzufügen
        this.element.appendChild(this.bigCover);
    }

    /**
     * Aktualisiert das Cover-Element. (void - Funktion)
     */
    updateCoverElement() {
        this.bigCoverImg.src  = bannerElement.src;     //Cover aktualisieren (identisch mit dem durch Player gesetzes Banner)
        this.bigCover.onclick = bannerElement.onclick; //onClick aktualisieren (identisch mit dem durch Player gesetze Banner-Element Aktion)
    }

    /**
     * Erstellt das Selektionsmenü für die verschiedenen Visualisierungsstile. (void - Funktion)
     */
    createStyleSelector() {

        //Select-Div
        let visualizationSelection = document.createElement("select");
        visualizationSelection.classList.add("app__visualize__select"); //CSS-Klasse

        //-- Optionen --
        for(const key in VisualizerStyles) {
            let option = document.createElement("option");
            option.innerText = "Stil: " + VisualizerStyles[key];
            option.value = VisualizerStyles[key];
            visualizationSelection.appendChild(option);
        }

        //Wenn User einen anderen Stil vom Drop-Down auswählt
        visualizationSelection.onchange = () => {
            VisualizeView_visualizer.setVisualizerStyle(visualizationSelection.value);
        };

        //Wenn "VisualizerStyle" bereits gesetzt wurde, den Wert übernehmen
        if (typeof VisualizerStyle !== 'undefined') {
            visualizationSelection.value = VisualizerStyle;
        }

        //Automatisch dem "element"-Attribut des Objekts hinzufügen
        this.element.appendChild(visualizationSelection);
    }

    /**
     * -- Konstruktor --
     */
    constructor() {

        //Äußeres <div> (benutze "element"-Attribut, damit dort automatisch andere Elemente angefügt werden können)
        this.element = document.createElement("div");
        this.element.classList.add("app__visualize"); //CSS-Klasse

        //Linkes Canvas-Element
        this.canvasLeft = this.createCanvasElement();

        this.createCoverElement(); //Cover-Element (wird im "bigCover"-Attribut gespeichert)
        this.updateCoverElement(); //Update des Cover-Elements

        //Rechtes Canvas-Element
        this.canvasRight = this.createCanvasElement();

        //Beide Canvas-Kontexte (2D) festlegen
        this.canvasLeftContext  = this.canvasLeft.getContext("2d");
        this.canvasRightContext = this.canvasRight.getContext("2d");

        //Die Stil-Auswahl erstellen
        this.createStyleSelector();
    }
}

//==================================================================================================================================================================
//-- Visualisierung direkt --

//Mögliche Visualisierer-Stile (Interner_Name:Anzeige Name)
const VisualizerStyles = {
    Balken_normal: "Balken (normal)",
    Balken_vShape: "Balken (V-Shape)",
    Sinus        : "Sinus",
    Speaker      : "Speaker",
    Pulsierend   : "Pulsierend",
    StaticWave   : "Static Wave"
}

//Aktueller Stil des Visualisierer
var VisualizerStyle = VisualizerStyles.Balken_normal;

class Visualizer {

    /**
     * Setzt die Variable "VisualizerStyle" und ändert die Canvas entsprechend ab. (void - Funktion)
     * @param VisualizerStyle Ein Wert aus "VisualizerStyles"
     */
    setVisualizerStyle(style) {
        VisualizerStyle = style;

        if(
            VisualizerStyle === VisualizerStyles.Balken_normal
            || VisualizerStyle === VisualizerStyles.Balken_vShape
            || VisualizerStyle === VisualizerStyles.StaticWave
        ) {
            VisualizeView_container.changeBorders(false);
        } else if(
            VisualizerStyle === VisualizerStyles.Sinus
            ||  VisualizerStyle === VisualizerStyles.Speaker
            ||  VisualizerStyle === VisualizerStyles.Pulsierend
        ) {
            VisualizeView_container.changeBorders(true);
        }
    }

    /**
     * Füllt die Canvas mit Hintergrundfarben aus bzw. entfernt aktuellen Inhalt. (void - Funktion)
     */
    emptyCanvases() {
        //Hintergrundfarbe (eigene)
        let bg = "#0a0a0a";

        this.canvasContextLeft.fillStyle = bg;
        this.canvasContextRight.fillStyle = bg;

        this.canvasContextLeft.fillRect(0,0,this.canvasContextLeft.canvas.width,this.canvasContextLeft.canvas.height);
        this.canvasContextRight.fillRect(0,0,this.canvasContextRight.canvas.width,this.canvasContextRight.canvas.height);
    }

    /**
     * -- Konstruktor --
     * @param CanvasContext Canvas-Kontext des linken Canvas
     * @param CanvasContext Canvas-Kontext des rechten Canvas
     */
    constructor(canvasContextLeft,canvasContextRight) {
        this.canvasContextLeft  = canvasContextLeft;
        this.canvasContextRight = canvasContextRight;

        //Die Canvas leeren bzw. den Hintergrund setzen
        this.emptyCanvases();

        //Audio-Processing-Kontext
        this.context = new (window.AudioContext || window.webkitAudioContext)(); //Manche Browser benötigen "webkit" davor

        //Der Analyzer
        this.analyzer = this.context.createAnalyser();

        //Quelle des Audio (muss AudioNode implementieren)
        //=> Erstelle aus dem Audio der Player-Konstante (HTMLMediaElement) einen kompatiblen "AudioNode" (MediaElementAudioSourceNode)
        this.source = this.context.createMediaElementSource(webplayer.audio);

        //Verbinde die Audio-Quelle mit dem Analyzer
        this.source.connect(this.analyzer);

        //Verbinde Analyzer mit der Audio-Ausgabe (Endgerät-Lautsprecher), was über den Context bekannt ist
        this.analyzer.connect(this.context.destination);

        //Stil festlegen
        this.setVisualizerStyle(VisualizerStyle);

        //Visualisierung ausführen
        this.visualize();
    }

    /**
     * Visualisiert das Audio in den Canvas-Elementen. (void - Funktion)
     */
    visualize() {

        /**
         * Setzt das Attribut "drawVisual" bzw. startet einen weiteren Frame für die Visualisierung. (void - Funktion)
         */
        const setDrawVisual = () => {
            this.drawVisual = (window.requestAnimationFrame || window.webkitRequestAnimationFrame)(() => { selectVisual(); });
        };

        //==================================================================================================
        //-- Stile --

        /**
         * Zeichnet Balken mit normalen Höhen. (void - Funktion)
         */
        const drawBars_normal = () => {
            setDrawVisual();

            //-- Generelle Einstellungen --
            this.analyzer.fftSize = 1024;                            //Sozusagen die Auflösung
            let bufferLength      = this.analyzer.frequencyBinCount; //Buffer
            let dataArray         = new Uint8Array(bufferLength);    //Daten

            const space    = 3;   //Wie viel Platz zwischen den Balken sein soll
            const barWidth = 2.5; //Breite eines Balkens ; Alte Berechnung: (WIDTH / bufferLength) * 2.5
            let barHeight  = 0;   //Höhe offen
            let x = 0;            //x-Koordinate eines Balkens im Canvas

            //Kopiert aktuelle Frequenzdaten in angegebenes Array
            this.analyzer.smoothingTimeConstant = 0.8;
            this.analyzer.minDecibels = -100;
            this.analyzer.maxDecibels = -30;
            this.analyzer.getByteFrequencyData(dataArray);
    
            //Vorherigen Draw entfernen
            this.emptyCanvases();

            //-- Zeichnen --
            for (let i = 0; i < bufferLength; i++) {
                barHeight = dataArray[i];

                this.canvasContextLeft.fillStyle = "#ff0000";
                this.canvasContextLeft.fillRect(x, HEIGHT - barHeight / 2, barWidth, barHeight / 2);

                this.canvasContextRight.fillStyle = "#ff0000";
                this.canvasContextRight.fillRect(WIDTH - (x + barWidth), HEIGHT - barHeight / 2, barWidth, barHeight / 2);

                x += barWidth + space;
            }

            //Prüfe, ob weiter Durchlauf gezeichnet werden soll
            checkIfCancel(dataArray);
        };

        /**
         * Zeichnet Balken in V-Form. (void - Funktion)
         */
        const drawBars_vShape = () => {
            setDrawVisual();

            //-- Generelle Einstellungen --
            this.analyzer.fftSize = 1024;                            //Sozusagen die Auflösung
            let bufferLength      = this.analyzer.frequencyBinCount; //Buffer
            let dataArray         = new Uint8Array(bufferLength);    //Daten

            const nth      = 3;   //Grenzt die Anzahl der Balken ein
            const space    = 3;   //Wie viel Platz zwischen den Balken sein soll
            const barWidth = 2.5; //Breite eines Balkens ; Alte Berechnung: (WIDTH / (bufferLength / nth))
            let barHeight  = 0;   //Höhe offen
            let x = 0;            //x-Koordinate eines Balkens im Canvas

            //Kopiert aktuelle Frequenzdaten in angegebenes Array
            this.analyzer.smoothingTimeConstant = 0.8;
            this.analyzer.minDecibels = -100;
            this.analyzer.maxDecibels = -30;
            this.analyzer.getByteFrequencyData(dataArray);

            //Vorherigen Draw entfernen
            this.emptyCanvases();
    
            //-- Zeichnen --
            for(let i = nth; i < bufferLength; i += nth) {

                //Neue Berechnung der Höhe eines Balkens:
                let dataMax = 255; //Maximum, was im dataArray sein kann (Zahlen von 0 bis 255 pro Element im Array).
                let barPercent = (100 * dataArray[i]) / dataMax; //Wie viel Prozent (von dataMax) das aktuelle dataArray-Element entspricht.
                barHeight = (barPercent * HEIGHT) / 100; //Berechne wie viele Pixel (Höhe des Balken) die Prozent entsprechen (beispielsweise barPercent = 98% => 98% von der Canvas-Höhe).
                //Die maximale Höhe eines Balkens ist die Canvas Höhe.
    
                let r = dataArray[i] + (25 * (i/(bufferLength / nth)));
                let g = 250 * (i/(bufferLength / nth));
                let b = 50;
    
                this.canvasContextLeft.fillStyle = "rgb(" + r + "," + g + "," + b + ")";
                this.canvasContextLeft.fillRect(x, HEIGHT - barHeight, barWidth, barHeight);
    
                this.canvasContextRight.fillStyle = "rgb(" + r + "," + g + "," + b + ")";
                this.canvasContextRight.fillRect(WIDTH - (x + barWidth), HEIGHT - barHeight, barWidth, barHeight);
    
                x += barWidth + space;
            }
    
            //Prüfe, ob weiter Durchlauf gezeichnet werden soll
            checkIfCancel(dataArray);
        };

        /**
         * Zeichnet Sinus. (void - Funktion)
         */
        const drawSinewave = () => {
            setDrawVisual();

            //-- Generelle Einstellungen --
            this.analyzer.fftSize = 2048;                         //Sozusagen die Auflösung
            let bufferLength      = this.analyzer.fftSize;        //Buffer
            let dataArray         = new Uint8Array(bufferLength); //Daten

            const waveWidth  = 4;                            //Wie dick die Welle minimal ist
            const waveColor  = "#ff0000";                    //Farbe der Welle
            const sliceWidth = (WIDTH * 1.0) / bufferLength; //Wie groß ein Wellen-Abschnitt sein soll

            let x_l = 0;     //X-Koordinate für linkes Canvas (startet links, also bei 0)
            let x_r = WIDTH; //X-Koordinate für rechtes Canvas (startet rechts, also bei letzter Koordinate => Breite des Canvas)

            //Kopiert aktuelle Waveform in angegebenes Array
            this.analyzer.getByteTimeDomainData(dataArray);

            //Vorherigen Draw entfernen
            this.emptyCanvases();

            //-- Zeichnen --
            this.canvasContextLeft.lineWidth    = waveWidth;
            this.canvasContextLeft.strokeStyle  = waveColor;
            this.canvasContextRight.lineWidth   = waveWidth;
            this.canvasContextRight.strokeStyle = waveColor;
    
            this.canvasContextLeft.beginPath();
            this.canvasContextRight.beginPath();
    
            for (let i = 0; i < bufferLength; i++) {
                const v = dataArray[i] / 128.0;
                const y = (v * HEIGHT) / 2;
    
                if (i === 0) {
                    this.canvasContextLeft.moveTo(x_l, y);
                    this.canvasContextRight.moveTo(x_r, y);
                } else {
                    this.canvasContextLeft.lineTo(x_l, y);
                    this.canvasContextRight.lineTo(x_r, y);
                }
    
                x_l += sliceWidth; //nach links gehen (+ Slice)
                x_r -= sliceWidth; //nach rechts gehen (- Slice)
            }
    
            this.canvasContextLeft.lineTo(WIDTH,HEIGHT / 2); //Linie endet rechts (also bei Breite des Canvas)
            this.canvasContextLeft.stroke();
            this.canvasContextRight.lineTo(0,HEIGHT / 2); //Linie endet links (also bei 0)
            this.canvasContextRight.stroke();

            //Prüfe, ob weiter Durchlauf gezeichnet werden soll
            checkIfCancel(dataArray);
        };

        /**
         * Zeichnet Balken in runder Anordnung, die wie Lautsprecher pulsieren. (void - Funktion)
         */
        const drawSpeaker = () => {
            setDrawVisual();

            //-- Generelle Einstellungen --
            this.analyzer.fftSize = 512;                             //Sozusagen die Auflösung
            let bufferLength      = this.analyzer.frequencyBinCount; //Buffer
            let dataArray         = new Uint8Array(bufferLength);    //Daten

            const barWidth   = 2; //Breite eines Balkens
            const barHeight  = 1; //Minimale Höhe eines Balkens
            const barSpacing = 3; //Abstand zwischen den Balken

            //Alternativ (füllt nicht den gesamten Kreis aus)
            //this.analyzer.smoothingTimeConstant = 0.6;
            //this.analyzer.minDecibels = -100;
            //this.analyzer.maxDecibels = -30;
            //this.analyzer.getByteFrequencyData(dataArray);

            //Kopiert aktuelle Waveform in angegebenes Array
            this.analyzer.getByteTimeDomainData(dataArray);

            //Vorherigen Draw entfernen
            this.emptyCanvases();

            //-- Zeichnen --
            this.canvasContextLeft.fillStyle  = "#ff0000";
            this.canvasContextRight.fillStyle = "#ff0000";

            var cx = WIDTH / 2;
            var cy = HEIGHT / 2;
            var radius = 46; //Radius des Kreises
            var maxBarNum = Math.floor((radius * 2 * Math.PI) / (barWidth + barSpacing)); //Wie wiele Balken möglich sind
            var freqJump  = Math.floor(bufferLength / maxBarNum);

            for (var i = 0; i < maxBarNum; i++) {

                //Ausschlag und Rotation eines Balkens
                var amplitude = dataArray[i * freqJump];
                var alfa = (i * 2 * Math.PI ) / maxBarNum;
                var beta = (3 * 45 - barWidth) * Math.PI / 180;
                var x = 0;
                var y = radius - (amplitude / 12 - barHeight);
                var w = barWidth;
                var h = amplitude / 6 + barHeight;

                this.canvasContextLeft.save();
                this.canvasContextLeft.translate(cx + barSpacing, cy + barSpacing);
                this.canvasContextLeft.rotate(alfa - beta);
                this.canvasContextLeft.fillRect(x, y, w, h);
                this.canvasContextLeft.restore();

                this.canvasContextRight.save();
                this.canvasContextRight.translate(cx + barSpacing, cy + barSpacing);
                this.canvasContextRight.rotate(alfa - beta);
                this.canvasContextRight.fillRect(x, y, w, h);
                this.canvasContextRight.restore();
            }

            //Prüfe, ob weiter Durchlauf gezeichnet werden soll
            checkIfCancel(dataArray);
        }

        /**
         * Zeichnet pulsierende Kreise. (void - Funktion)
         */
        const drawPulsatingCircle = () => {
            setDrawVisual();

            //-- Generelle Einstellungen --
            this.analyzer.fftSize = 2048;                            //Sozusagen die Auflösung
            let bufferLength      = this.analyzer.frequencyBinCount; //Buffer
            let dataArray         = new Uint8Array(bufferLength);    //Daten

            const scale = 0.35; //Dient dazu den gezeichneten Kreis auf bestimmtes Maß zu verkleinern

            //Kopiert aktuelle Waveform in angegebenes Array
            this.analyzer.getByteTimeDomainData(dataArray);

            //Vorherigen Draw entfernen
            this.emptyCanvases();

            //-- Zeichnen --

            this.canvasContextLeft.fillStyle  = "#ff0000";
            this.canvasContextRight.fillStyle = "#ff0000";

            //X- und Y-Koordinate für Kreis-Ursprung
            let cX = WIDTH / 2;
            let cY = HEIGHT / 2;

            //Winkel
            let radian = 0;
            let radianAdd = TWO_PI * (1.0 / dataArray.length);

            for(let i = 0; i < dataArray.length; i++) {
                let v = dataArray[i];
                v = v * scale;

                let x = v * Math.cos(radian) + cX;
                let y = v * Math.sin(radian) + cY;

                this.canvasContextLeft.beginPath();
                this.canvasContextLeft.arc(x,y,2,0,TWO_PI,false);
                this.canvasContextLeft.fill();

                this.canvasContextRight.beginPath();
                this.canvasContextRight.arc(x,y,2,0,TWO_PI,false);
                this.canvasContextRight.fill();

                radian += radianAdd;
            }

            //Prüfe, ob weiter Durchlauf gezeichnet werden soll
            checkIfCancel(dataArray);
        }

        /**
         * Zeichnet eine statische Waveform. (void - Funktion)
         */
        const drawStaticWaveform = () => {
            setDrawVisual();

            //-- Generelle Einstellungen --
            this.analyzer.fftSize = 1024;                            //Sozusagen die Auflösung
            let bufferLength      = this.analyzer.frequencyBinCount; //Buffer
            let dataArray         = new Uint8Array(bufferLength);    //Daten

            const nth    = 6;
            const margin = 60;
            const centerHeight = Math.ceil(HEIGHT / 2);
            const scaleFactor  = (HEIGHT - (margin * 2)) / 2;

            //Kopiert aktuelle Waveform in angegebenes Array
            this.analyzer.smoothingTimeConstant = 0.8;
            this.analyzer.minDecibels = -85;
            this.analyzer.maxDecibels = -30;
            this.analyzer.getByteFrequencyData(dataArray);

            //Vorherigen Draw entfernen
            this.emptyCanvases();

            this.canvasContextLeft.strokeStyle = "#ff0000";
            this.canvasContextRight.strokeStyle = "#ff0000";
            this.canvasContextLeft.lineWidth = 2;
            this.canvasContextRight.lineWidth = 2;

            for (let i = nth ; i < dataArray.length; i += nth) {
                let v = dataArray[i] * 0.022;

                //Verhindere leeren Raum im Canvas
                if(v === 0) {
                    v = 0.1;
                }

                this.canvasContextLeft.beginPath();
                this.canvasContextLeft.moveTo(i, centerHeight - (v * scaleFactor));
                this.canvasContextLeft.lineTo(i, centerHeight + (v * scaleFactor));
                this.canvasContextLeft.stroke();

                this.canvasContextRight.beginPath();
                this.canvasContextRight.moveTo(WIDTH - i, centerHeight - (v * scaleFactor));
                this.canvasContextRight.lineTo(WIDTH - i, centerHeight + (v * scaleFactor));
                this.canvasContextRight.stroke();
            }

            //Prüfe, ob weiter Durchlauf gezeichnet werden soll
            checkIfCancel(dataArray);
        };

        //==================================================================================================
        //-- Generelles --

        /**
         * Prüft, ob die Endlosschleife in den "draw"-Funktionen unterbrochen werden kann. Wenn ja, wird unterbrochen. (void - Funktion)
         */
        const checkIfCancel = (givenDataArray) => {

            /**
             * Fügt einen Event-Listener zum Webplayer-Audio hinzu, der einmalig auslöst, wenn die Wiedergabe fortgesetzt wird. (void - Funktion)
             * Das sorgt dafür, dass der Visualizer wieder Startet, wenn Wiedergabe fortgesetzt wird
             */
            const setContinueVisualizeListener = () => {
                webplayer.audio.addEventListener("play",() => { this.visualize(); },{ once: true });
            }

            //-- Wann beendet werden kann hängt von der Visualisierungart ab --
            if(
                VisualizerStyle === VisualizerStyles.Balken_normal
                || VisualizerStyle === VisualizerStyles.Balken_vShape
                || VisualizerStyle === VisualizerStyles.StaticWave
            ) {
                //Wenn Audio pausiert ist UND jeder Eintrag im Daten-Array 0 ist
                if(webplayer.audio.paused && givenDataArray.every(value => value === 0)) {
                    this.cancelAnimationFrame_();
                    setContinueVisualizeListener();
                }
            } else if(
                VisualizerStyle == VisualizerStyles.Sinus
                || VisualizerStyle === VisualizerStyles.Speaker
                || VisualizerStyle === VisualizerStyles.Pulsierend
            ) {
                //Wenn Audio pausiert ist UND jeder Eintrag im Daten-Array 128 ist
                if(webplayer.audio.paused && givenDataArray.every(value => value === 128)) {
                    this.cancelAnimationFrame_();
                    setContinueVisualizeListener();
                }
            }
        };

        /**
         * Wählt den ensprechenden Visualisierungs-Sil aus und startet das Zeichnen mit dem entsprechenden Stil für einen Durchlauf. (void - Funktion)
         */
        const selectVisual = () => {
            if(VisualizerStyle === VisualizerStyles.Balken_normal) {
                drawBars_normal();
            } else if(VisualizerStyle === VisualizerStyles.Balken_vShape) {
                drawBars_vShape();
            } else if(VisualizerStyle == VisualizerStyles.Sinus) {
                drawSinewave();
            } else if(VisualizerStyle == VisualizerStyles.Speaker) {
                drawSpeaker();
            } else if(VisualizerStyle == VisualizerStyles.Pulsierend) {
                drawPulsatingCircle();
            } else if(VisualizerStyle == VisualizerStyles.StaticWave) {
                drawStaticWaveform();
            }
        };

        //Breite und Höhe von den Canvas merken
        const WIDTH  = this.canvasContextLeft.canvas.width;
        const HEIGHT = this.canvasContextLeft.canvas.height;

        //Mathematische Konstante für (PI * 2)
        const TWO_PI = 6.28318530717958647693;

        //Aktuelle ID von "requestAnimationFrame"
        this.drawVisual = null;

        //Verhindere Draw, wenn auf Seite und kein Track geladen
        if(!webplayer.audio.paused) {
            selectVisual();
        }
    }

    /**
     * Breche den geplanten Draw-Request ab und unterbreche damit die aufgebaute Dauerschleife. (void - Funktion)
     */
    cancelAnimationFrame_() {
        window.cancelAnimationFrame(this.drawVisual);
    }
}