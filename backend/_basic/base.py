########################################################################################################################################################################
#
# Basisklassen, auf denen alles aufbaut
#
########################################################################################################################################################################

########################################################################################################################################################################
# -- BasicType --
# Basis-Klasse für Kategorien / Typen an verschiedenen Radiotracks-Angeboten.
# Diese Attribute hat jedes Angebot auf Radiotracks (Alben, Channel, Podcasts etc.).
# Diese Klasse ist als abstrakt zu verstehen, muss also geerbt und erweitert/überschrieben werden, damit sie richtig genutzt werden kann.

class BasicType:

    #-- Konstruktor --
    def __init__(self):
        self.id        = "" #Eindeutige ID
        self.name      = "" #Ein Name
        self.path      = "" #Gesamter Pfad auf dem Dateisystem
        self.mediaPath = "" #Pfad innerhalb des "media/"-Ordners
        self.cover     = "" #Pfad des Covers im Ordner des "media/"-Ordners

    #Stringrepräsentation
    def __repr__(self):
        r  = "\n-- BasicType --\n"
        r += "id       : " + str(self.id) + "\n"
        r += "name     : " + str(self.name) + "\n"
        r += "path     : " + str(self.path) + "\n"
        r += "mediaPath: " + str(self.mediaPath) + "\n"
        r += "cover    : " + str(self.cover) + "\n"
        return r

    #Gleichheit
    def __eq__(self,other):
        return self.id     == other.id \
        and self.name      == other.name \
        and self.path      == other.path \
        and self.mediaPath == other.mediaPath \
        and self.cover     == other.cover

    #Wandelt in ein Dictionary um
    #@return Dict Object als Dictionary
    def toDict(self):
        d = dict()

        d["id"]        = self.id
        d["name"]      = self.name
        d["path"]      = self.path
        d["mediaPath"] = self.mediaPath
        d["cover"]     = self.cover

        return d

    #Erstellt ein BasicType-Objekt aus den Werten, die aus der Datenbank abgefragt wurden.
    #@param Tuple      Das Tuple, welches von der Datenbank zurückgegeben wurde
    #@return BasicType Ein BasicType-Objekt
    def fromDBTuple(databaseTuple):
        b = BasicType()

        b.id        = databaseTuple[0]
        b.name      = databaseTuple[1]
        b.path      = databaseTuple[2]
        b.mediaPath = databaseTuple[3]
        b.cover     = databaseTuple[4]

        return b

########################################################################################################################################################################
# -- Audio-Dateien --
# Klassen für Audio-Dateien.

#Für alle Art Audio-Dateien
class AudioFile:

    #-- Konstruktor --
    def __init__(self):
        self.path      = "" #Gesamter Pfad der Datei auf dem Dateisystem
        self.mediaPath = "" #Pfad innerhalb des "media/"-Ordners
        self.filename  = "" #Dateiname mit Dateiendung
        self.duration  = 0  #Dauer (in Sekunden)

    #Stringrepräsentation
    def __repr__(self):
        r  = "\n-- AudioFile --\n"
        r += "path     : " + str(self.path) + "\n"
        r += "mediaPath: " + str(self.mediaPath) + "\n"
        r += "filename : " + str(self.filename) + "\n"
        r += "duration : " + str(self.duration) + "\n"
        return r

    #Gleichheit
    def __eq__(self,other):
        return self.path   == other.path \
        and self.mediaPath == other.mediaPath \
        and self.filename  == other.filename \
        and self.duration  == other.duration

    #Wandelt in ein Dictionary um
    #@return Dict Object als Dictionary
    def toDict(self):
        audioFileDict = dict()

        audioFileDict["path"]      = self.path
        audioFileDict["mediaPath"] = self.mediaPath
        audioFileDict["filename"]  = self.filename
        audioFileDict["duration"]  = self.duration
        
        return audioFileDict

    #Erstellt ein AudioFile-Objekt aus einem Dictionary
    #@param Dict       Ein Dictionary mit allen Attributen für ein AudioFile-Objekt (aus der Datenbank)
    #@return AudioFile Ein AudioFile-Objekt
    def fromDict(audioFileDict):
        audioFile           = AudioFile()
        audioFile.path      = audioFileDict["path"]
        audioFile.mediaPath = audioFileDict["mediaPath"]
        audioFile.filename  = audioFileDict["filename"]
        audioFile.duration  = audioFileDict["duration"]

        return audioFile

    #Erstellt eine Liste mit AudioFile-Objekten
    #@param List  Eine Liste mit AudioFile-Dictionaries mit allen Attributen für ein AudioFile-Objekt (aus der Datenbank)
    #@return List Liste mit AudioFile-Objekten / leere Liste, wenn übergebene Liste leer ist
    def batchCreate(listOfAudioFileDicts):
        audioFileObjects = list()
        for audioFileDict in listOfAudioFileDicts:
            audioFileObjects.append(AudioFile.fromDict(audioFileDict))
        return audioFileObjects

#Erweiterte AudioFile-Klasse
class AudioTrack(AudioFile):

    #-- Konstruktor --
    def __init__(self):
        super().__init__()
        self.title = ""

    #Überschreibe "Stringrepräsentation"
    def __repr__(self):
        r = super().__repr__()
        r += "-- AudioTrack --\n"
        r += "title: " + str(self.title) + "\n"
        return r

    #Überschreibe "equals"
    def __eq__(self,other):
        return super().__eq__(self,other) \
        and self.title == other.title

    #Überschreibe "toDict"
    def toDict(self):
        d = super().toDict()
        d["title"] = self.title
        return d

    #Erstellt ein AudioTrack-Objekt aus den Werten, die aus der Datenbank abgefragt wurden.
    #@param Tuple       Das Tuple, welches von der Datenbank zurückgegeben wurde
    #@return AudioTrack Ein AudioTrack-Objekt
    def fromDBTuple(databaseTuple):
        at           = AudioTrack()
        at.path      = databaseTuple[0]
        at.mediaPath = databaseTuple[1]
        at.filename  = databaseTuple[2]
        at.duration  = databaseTuple[3]
        at.title     = databaseTuple[4]

        return at

    #Überschreibe "fromDict"
    def fromDict(audioTrackDict):
        audioTrack           = AudioTrack()
        audioTrack.path      = audioTrackDict["path"]
        audioTrack.mediaPath = audioTrackDict["mediaPath"]
        audioTrack.filename  = audioTrackDict["filename"]
        audioTrack.duration  = audioTrackDict["duration"]
        audioTrack.title     = audioTrackDict["title"]

        return audioTrack

    #Überschreibe "batchCreate"
    def batchCreate(listOfAudioTrackDicts):
        audioTrackObjects = list()
        for audioTrackDict in listOfAudioTrackDicts:
            audioTrackObjects.append(AudioTrack.fromDict(audioTrackDict))
        return audioTrackObjects

########################################################################################################################################################################
# -- Audio-Zusammenfassung --
# Klassen für Audio-Zusammenfassung.

#Audio-Collectionen (für z.B. Alben, Audio-Books etc.)
#Diese Klasse ist als abstrakt zu verstehen, muss also geerbt und erweitert werden.
class AudioCollection(BasicType):

    #-- Konstruktor --
    def __init__(self):
        super().__init__()
        self.published  = "init" #Wann die Collection veröffentlicht wurde ("name" muss "(YYYY) Collection-Name" sein)
        self.tracks     = list() #Liste mit "AudioTrack"-Objekten
        self.trackCount = 0      #Wie viele Tracks die Collection hat
        self.duration   = 0      #Wie lang die Spielzeit der Collection ist (in Sekunden)

    #Überschreibe "Stringrepräsentation"
    def __repr__(self):
        r  = super().__repr__()
        r += "-- AudioCollection --\n"
        r += "published : " + str(self.published) + "\n"
        r += "tracks    : " + str(self.tracks) + "\n"
        r += "trackCount: " + str(self.trackCount) + "\n"
        r += "duration  : " + str(self.duration) + "\n"
        return r

    #Überschreibe "equals"
    def __eq__(self,other):
        return super().__eq__(self,other) \
        and self.published  == other.published \
        and self.tracks     == other.tracks \
        and self.trackCount == other.trackCount \
        and self.duration   == other.duration

    #Überschreibe "toDict"
    def toDict(self):
        audioCollectionDict = super().toDict()
        
        audioCollectionDict["published"]  = self.published
        audioCollectionDict["tracks"]     = list()
        for track in self.tracks:
            audioCollectionDict["tracks"].append(track.toDict())
        audioCollectionDict["trackCount"] = self.trackCount
        audioCollectionDict["duration"]   = self.duration
        
        return audioCollectionDict

    #Erstellt ein AudioCollection-Objekt aus den Werten, die aus der Datenbank abgefragt wurden.
    #@param Tuple            Das Tuple, welches von der Datenbank zurückgegeben wurde
    #@param bool             Ob das ID-Attribut der AudioCollection in der Datenbankrückgabe an Index-Stelle 0 steht (OPTIONAL)
    #@return AudioCollection Ein AudioCollection-Objekt
    def fromDBTuple(databaseTuple,idAtIndex0 = False):

        if idAtIndex0:
            b = BasicType.fromDBTuple(databaseTuple)
        else:
            b = BasicType.fromDBTuple(databaseTuple[1:6])

        ac = AudioCollection()

        #BasicType-Attribute
        ac.id        = b.id
        ac.name      = b.name
        ac.path      = b.path
        ac.mediaPath = b.mediaPath
        ac.cover     = b.cover

        #AudioCollection-Attribute
        ac.published  = databaseTuple[5 if idAtIndex0 else 6]
        #"tracks" muss anders zugewiesen werden

        #Je nachdem, welche Child-Klasse diese Methode aufruft
        if len(databaseTuple) == 9:
            #Album
            ac.trackCount = databaseTuple[7]
            ac.duration   = databaseTuple[8]
        elif len(databaseTuple) == 11:
            #AudioBook
            ac.trackCount = databaseTuple[8]
            ac.duration   = databaseTuple[9]
        elif len(databaseTuple) == 12:
            #CuratedPlaylist
            ac.trackCount = databaseTuple[7]
            ac.duration   = databaseTuple[8]

        return ac

#Creators (z.B. Artists, Authors etc.)
#Diese Klasse ist als abstrakt zu verstehen, muss also geerbt und erweitert werden.
class AudioCreator(BasicType):

    #-- Konstruktor --
    def __init__(self):
        super().__init__()
        self.audioCollections     = list() #Liste mit "AudioCollection"-Objekten bzw. deren Unterklassen
        self.audioCollectionCount = 0      #Anzahl der "AudioCollection"-Objekte bzw. deren Unterklassen

    #Überschreibe "Stringrepräsentation"
    def __repr__(self):
        r  = super().__repr__()
        r += "-- AudioCreator --\n"
        r += "audioCollections    : " + str(self.audioCollections) + "\n"
        r += "audioCollectionCount: " + str(self.audioCollectionCount) + "\n"
        return r

    #Überschreibe "equals"
    def __eq__(self,other):
        return super().__eq__(self,other) \
        and self.audioCollections     == other.audioCollections \
        and self.audioCollectionCount == other.audioCollectionCount

    #Überschreibe "toDict"
    def toDict(self):
        audioCreatorDict = super().toDict()

        audioCreatorDict["audioCollections"] = list()
        for audioCollection in self.audioCollections:
            audioCreatorDict["audioCollections"].append(audioCollection.toDict())
        audioCreatorDict["audioCollectionCount"] = self.audioCollectionCount

        return audioCreatorDict

    #Erstellt ein AudioCreator-Objekt aus den Werten, die aus der Datenbank abgefragt wurden.
    #@param Tuple         Das Tuple, welches von der Datenbank zurückgegeben wurde
    #@return AudioCreator Ein AudioCreator-Objekt
    def fromDBTuple(databaseTuple):
        b = BasicType.fromDBTuple(databaseTuple)

        ac = AudioCreator()

        #BasicType-Attribute
        ac.id        = b.id
        ac.name      = b.name
        ac.path      = b.path
        ac.mediaPath = b.mediaPath
        ac.cover     = b.cover

        #AudioCreator-Attribute
        #"audioCollections" muss anders zugewiesen werden
        ac.audioCollectionCount = databaseTuple[5]

        return ac