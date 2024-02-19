########################################################################################################################################################################
#
# Mixer für AdvancedChannel (erstellt AdvancedMix-Objekte)
#
########################################################################################################################################################################

import copy
import time
import json
import math

from _basic import getSetting, AudioFile, RadiotracksDBConnection, RadiotracksLog, getRandomness, getRandomItemFromList

from .mix import AdvancedMix

########################################################################################################################################################################

class AdvancedMixer:
    #-- Statische Felder / Einstellungen => gelten für alle AdvancedMixer-Objekte --

    #Einstellungen für Mixer
    announceLikeliness          = None
    interceptionLikeliness      = None
    maximumConsecutiveSongCount = None
    maximumConsecutiveAdCount   = None
    neededMixLength             = None

    #Initialisiert die statischen Felder mit den entsprechenden Werten. (void - Funktion)
    def loadSettings():
        AdvancedMixer.announceLikeliness          = getSetting("hosting")["announceLikeliness"]
        AdvancedMixer.interceptionLikeliness      = getSetting("hosting")["interceptionLikeliness"]
        AdvancedMixer.maximumConsecutiveSongCount = getSetting("hosting")["maximumConsecutiveSongCount"]
        AdvancedMixer.maximumConsecutiveAdCount   = getSetting("hosting")["maximumConsecutiveAdCount"]
        AdvancedMixer.neededMixLength             = getSetting("hosting")["neededMixLength"]

        RadiotracksLog.log("AdvancedMixer","Settings loaded")

    ########################################################################################################################################################################
    #-- Generelles zur Klasse --

    #-- Konstruktor --
    #@param AdvancedChannel Ein AdvancedChannel-Objekt (wird kopiert, sodass das originale Objekt unberührt bleibt)
    def __init__(self,advancedChannelObject):
        self.advancedChannel = None   #Das assoziierte AdvancedChannel-Objekt (KOPIE)
        self.tracks          = list() #Liste mit AudioFile-Objekten
        self.duration        = 0      #Spieldauer des Mix in Sekunden
        self.rdbc            = RadiotracksDBConnection() #Ein "RadiotracksDBConnection"-Objekt, um mit der Datenbank zu kommunizieren

        #Kopie des übergebenen AdvancedChannel-Objekts speichern
        self.advancedChannel = copy.deepcopy(advancedChannelObject)
    
    #Stringrepräsentation
    def __repr__(self):
        r  = "\n-- AdvancedMixer --\n"
        r += "advancedChannel : " + str(self.advancedChannel) + "\n"
        r += "tracks          : " + str(self.tracks) + "\n"
        r += "duration        : " + str(self.duration) + "\n"
        return r

    #Fügt eine AudioFile der "tracks"-List hinzu und updated die "duration". (void - Funktion)
    #@param AudioFile Ein AudioFile-Objekt
    def appendToTracks(self,audioFileToAppend):
        if audioFileToAppend is not None:
            self.tracks.append(audioFileToAppend)
            self.duration += audioFileToAppend.duration

    ########################################################################################################################################################################
    #-- Methode von Außen --

    #Erstellt einen Mix für den AdvancedChannel
    #@return AdvancedMix Ein fertiges AdvancedMix-Objekt
    def createMix(self):

        #Besorgt Interceptions aus der Datenbank
        #@param String Ein Ordnername mit Interceptions
        #@param String Ein Interception-Typ (kann "adverts", "news" oder "weather" sein)
        #@return List  Liste mit AudioFile-Objekten / leere Liste, wenn kein Ordner angegeben wurde bzw. dieser keine Tracks enthält
        def getInterceptionSources(interceptionFolder,interceptionType):
            if interceptionType in ["adverts","news","weather"]:
                self.rdbc.databaseCursor.execute('SELECT `tracks` FROM `interceptionsources` WHERE `foldername` = ? AND `type` = ?',[interceptionFolder,interceptionType])
                interceptions = self.rdbc.databaseCursor.fetchall()
                if len(interceptions) > 0:
                    return AudioFile.batchCreate(json.loads(interceptions[0][0]))
                return []

        #Interceptions schon aus Datenbank laden
        newsTracks    = getInterceptionSources(self.advancedChannel.newsFolder,"news")
        advertTracks  = getInterceptionSources(self.advancedChannel.advertsFolder,"adverts")
        weatherTracks = getInterceptionSources(self.advancedChannel.weatherFolder,"weather")

        #So lange zusammenfügen, bis die benötigte Spieldauer erreicht wurde UND noch Tracks vorhanden sind, die hinzugefügt werden könnten
        while self.duration < AdvancedMixer.neededMixLength and len(self.advancedChannel.tracks) > 0:

            #ggf. einen Channel-ID-Track einspielen (sofern existiert)
            if getRandomness() <= AdvancedMixer.announceLikeliness:
                self.appendToTracks(getRandomItemFromList(self.advancedChannel.idTracks))

            #Musik einfügen (wenn noch verfügbar)
            for i in range(0,getRandomness(1,AdvancedMixer.maximumConsecutiveSongCount)):

                #Zufälliger Song (Track kann None sein!)
                songFile = getRandomItemFromList(self.advancedChannel.tracks,True)

                #Entscheide ob der Track angesagt wird, sofern nicht None
                if getRandomness() <= AdvancedMixer.announceLikeliness and songFile is not None:
                    #Musiktrack-Ansage hinzufügen (sofern existiert)
                    self.appendToTracks(getRandomItemFromList(self.advancedChannel.getIntrosForTrack(songFile)))

                #Zur Playlist hinzufügen
                self.appendToTracks(songFile)

                #Entscheide ob ein Outro für den Track gespielt wird, sofern nicht None
                if getRandomness() <= AdvancedMixer.announceLikeliness and songFile is not None:
                    #Musiktrack-Outro hinzufügen (sofern existiert)
                    self.appendToTracks(getRandomItemFromList(self.advancedChannel.getOutrosForTrack(songFile)))
            
            #ggf. eine Unterbrechung (News / Werbung / Wetter)
            #-> wird ignoriert, wenn keine entsprechende Unterbrechung vorhanden
            if getRandomness() <= AdvancedMixer.interceptionLikeliness:
                
                #Welche Art Unterbrechung
                #News    = 1,2,3
                #Werbung = 4,5,6,7
                #Wetter  = 8,9
                interceptionType = getRandomness(1,9)

                #ggf. die Unterbrechung ansagen (wird ignoriert, wenn kein Ansage-Track vorhanden)
                announceInterception = getRandomness() <= AdvancedMixer.announceLikeliness
                
                if interceptionType >= 1 and interceptionType <= 3:
                    if announceInterception:
                        self.appendToTracks(getRandomItemFromList(self.advancedChannel.toTracks["news"]))
                    self.appendToTracks(getRandomItemFromList(newsTracks,True))
                elif interceptionType >= 4 and interceptionType <= 7:
                    if announceInterception:
                        self.appendToTracks(getRandomItemFromList(self.advancedChannel.toTracks["adverts"]))
                    adCount = getRandomness(1,AdvancedMixer.maximumConsecutiveAdCount)
                    for i in range(0,adCount):
                        self.appendToTracks(getRandomItemFromList(advertTracks,True))
                elif interceptionType >= 8 and interceptionType <= 9:
                    if announceInterception:
                        self.appendToTracks(getRandomItemFromList(self.advancedChannel.toTracks["weather"]))
                    self.appendToTracks(getRandomItemFromList(weatherTracks,True))
            
            #ggf. eine Unterbrechung (Monolog / Zeitansage)
            #-> wird ignoriert, wenn keine entsprechende Unterbrechung vorhanden
            if getRandomness() <= AdvancedMixer.interceptionLikeliness:

                #Welche Art Unterbrechung
                #Monolog    = 1,2,3,4,5,6,7
                #Zeitansage = 8,9
                interceptionType = getRandomness(1,9)

                if interceptionType >= 1 and interceptionType <= 7:
                    self.appendToTracks(getRandomItemFromList(self.advancedChannel.monologueTracks,True))
                elif interceptionType >= 8 and interceptionType <= 9:
                    self.appendToTracks(getRandomItemFromList(self.advancedChannel.getTimeTracks()))

        self.rdbc.closeDatabaseConnection()

        #Fertig mit mixen -> AdvancedMix erstellen
        return AdvancedMix(self.advancedChannel.id,self.tracks,self.duration)