########################################################################################################################################################################
#
# Die Indexer-Klasse
#
########################################################################################################################################################################

import hashlib
import math
import json

from mutagen.mp3 import MP3
import jfiles

from _basic import RadiotracksLog, getSetting

#Indexer für verschiedene Typen
from .indexers.index_artists import IndexArtists
from .indexers.index_authors import IndexAuthors
from .indexers.index_channels import IndexChannels
from .indexers.index_curatedplaylists import IndexCuratedPlaylists
from .indexers.index_podcasts import IndexPodcasts

########################################################################################################################################################################

class Indexer:

    #Berechnet die Dauer in Sekunden einer MP3-Datei
    #@param String Pfad einer MP3-Datei
    #@return Int   Dauer in Sekunden
    def calculateDuration(aFilepath):
        d = 0
        if jfiles.getFilesize(aFilepath) > 0:
            d = MP3(aFilepath)
            d = math.floor(d.info.length)
        return d

    #Gibt den Teil des Pfad zurück, der in "media/" liegt
    #@param String  Pfad mit "media/" Teil
    #@return String "media/"-Teil des Pfads
    def generateMediaPath(aCompletePath):
        return aCompletePath[aCompletePath.rfind("media/"):]

    #-- Konstruktor --
    def __init__(self):
        self.mediaFolderPath = getSetting("indexing")["mediaFolderPath"]
        RadiotracksLog.log("Indexer","mediaFolderPath: " + self.mediaFolderPath)

    #-- Gemeinsame Methoden für verschiedene Indexer --

    #Generiert IDs für sämtliche Komponenten der Anwendung
    #@return String Hash
    def generateId(self,pathToHash):
        h = hashlib.md5(bytes(pathToHash,"utf8")) #MD5-Hash (Länge = 32)
        return h.hexdigest()
    
    #Findet Cover / Banner für Alben, Podcasts, Artists, Channel etc. in ihren jeweiligen Ordnern (zur Unterstützung mehrerer Dateitypen)
    #@param String  Pfad, in dem gesucht werden soll
    #@return String Name der Datei (es wird alphabetisch ausgesucht)
    def findCover(self,folderpath):
        #Alle Art Bilddateien
        allJPG = jfiles.getAllFilesInPath(folderpath,"jpg",False,False,False)
        allJPG.extend(jfiles.getAllFilesInPath(folderpath,"jpeg",False,False,False))
        allPNG = jfiles.getAllFilesInPath(folderpath,"png",False,False,False)
        allGIF = jfiles.getAllFilesInPath(folderpath,"gif",False,False,False)

        #Zusammenfassen
        allImageFiles = list()
        allImageFiles.extend(allJPG)
        allImageFiles.extend(allPNG)
        allImageFiles.extend(allGIF)

        #Neu sortieren
        allImageFiles.sort()
        
        return allImageFiles[0]
    
    #Jahresdatum der Herausgabe generieren
    #@param String  Ein Name nach der Syntax "(YYYY) Irgendein Name"
    #@return String Der "YYYY"-Teil
    def generatePublished(self,nameOfItem):
        return nameOfItem[1:5]

    #Name ohne Jahresdatum
    #@param String  Ein Name nach der Syntax "(YYYY) Irgendein Name"
    #@return String Der "Irgendein Name"-Teil
    def generateName(self,nameOfItem):
        return nameOfItem[7:]

    #Siehe "generateMediaPath()"-Methode
    def getMediaPath(self,completePath):
        return Indexer.generateMediaPath(completePath)

    #Siehe "calculateDuration()"-Methode
    def getDuration(self,filepath):
        return Indexer.calculateDuration(filepath)
    
    #Generiert einen Titel ohne Index-Zahl und Dateiendung
    #--> Gehe davon aus, dass Dateiname = "Zahl - Irgendein Name_mit $ egal - was.Dateiendung" ist
    #@param String  Pfad zur Audio-Datei
    #@return String Titel / leerer String, wenn nicht gefunden
    def generateTitle(self,pathOfAudioFile):
        #Dateiname (ohne Dateiendung)
        fn = jfiles.getFilenameNoExtension(pathOfAudioFile)

        #Finde "-" im Dateinamen
        t = fn.find("-")

        #Wenn "-" gefunden wurde
        if t > -1:
            #Index von "-" + 1 bis Ende und dann die Leerzeichen entfernen
            return str(fn[t + 1:]).strip()

        return ""

    #Liest die JSON-Dateien für Beschreibungen etc. ein (normalerweise "description.json")
    #@param String Gesamter Pfad des Ordners, in dem die Datei "description.json" liegt
    #@param String Name der Datei (ohne Dateiendung) (OPTIONAL)
    #@return Dict  Inhalt der JSON als Dictionary / leeres Dictionary bei Fehler
    def getDescriptionJson(self,pathWithDescriptionFile, filename = "description"):
        dJP = pathWithDescriptionFile + "/" + filename + ".json"
        dJ = jfiles.readInFile(dJP,"utf8")
        if dJ is not None:
            #Datei wurde gefunden und eingelesen
            dJ = json.loads(dJ)
        else:
            #Fehler
            dJ = dict()
        return dJ

    #-- Indexer-Aufrufe --

    def indexArtists(self):
        ia = IndexArtists(self)
        ia.index()
    
    def indexAuthors(self):
        ia = IndexAuthors(self)
        ia.index()
    
    def indexChannels(self):
        ic = IndexChannels(self)
        ic.index()
    
    def indexCuratedPlaylists(self):
        icp = IndexCuratedPlaylists(self)
        icp.index()
    
    def indexPodcasts(self):
        ip = IndexPodcasts(self)
        ip.index()