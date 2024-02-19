########################################################################################################################################################################
#
# Die Playlist / der fertige Mix eines AdvancedChannel (wird von AdvancedMixer-Objekten erstellt)
#
########################################################################################################################################################################

import time
import json

from _basic import AudioFile

########################################################################################################################################################################

class AdvancedMix:

    #-- Konstruktor --
    #@param String ID des AdvancedChannel, für den der Mix gilt
    #@param List   Liste mit AudioFile-Objekten
    #@param Int    Gesamtspieldauer des Mix in Sekunden
    def __init__(self,advancedChannelId,mixTracks,mixDuration):
        self.advancedChannelId = advancedChannelId #Siehe Parameter
        self.tracks            = mixTracks         #Siehe Parameter
        self.creationTime      = int(time.time())  #Unix-Zeitstempel, wann die Erstellung abgeschlossen wurde bzw. das Objekt erstellt wurde
        self.duration          = mixDuration       #Siehe Parameter
        
        #Unix-Zeitstempel, ab wann der Mix gültig ist (standardmäßig ab Erstellung)
        self.validFrom = self.creationTime 
        
        #Unix-Zeitstempel, ab wann der Mix ungültig ist
        self.validTo = 0
        self.updateValidTo()
    
    #Stringrepräsentation
    def __repr__(self):
        r  = "\n-- AdvancedMix --\n"
        r += "advancedChannelId: " + str(self.advancedChannelId) + "\n"
        r += "tracks           : " + str(self.tracks) + "\n"
        r += "creationTime     : " + str(self.creationTime) + "\n"
        r += "duration         : " + str(self.duration) + "\n"
        r += "validFrom        : " + str(self.validFrom) + "\n"
        r += "validTo          : " + str(self.validTo) + "\n"
        return r
    
    #Gleichheit
    def __eq__(self,other):
        return \
        self.advancedChannelId == other.advancedChannelId \
        and self.tracks        == other.tracks \
        and self.creationTime  == other.creationTime \
        and self.duration      == other.duration \
        and self.validFrom     == other.validFrom \
        and self.validTo       == other.validTo

    #Wandelt in ein Dictionary um
    #@return Dict Object als Dictionary
    def toDict(self):
        d = dict()

        d["advancedChannelId"] = self.advancedChannelId
        d["tracks"]            = [x.toDict() for x in self.tracks]
        d["creationTime"]      = self.creationTime
        d["duration"]          = self.duration
        d["validFrom"]         = self.validFrom
        d["validTo"]           = self.validTo

        return d

    #Erstellt ein AdvancedMix-Objekt aus den Werten, die aus der Datenbank abgefragt wurden.
    #@param Tuple        Das Tuple, welches von der Datenbank zurückgegeben wurde
    #@return AdvancedMix Ein AdvancedMix-Objekt
    def fromDBTuple(databaseTuple):
        am = AdvancedMix(databaseTuple[0],AudioFile.batchCreate(json.loads(databaseTuple[1])),databaseTuple[3])

        #Attribute entsprechend der Datenbankwerte anpassen
        am.creationTime = databaseTuple[2]
        am.validFrom    = databaseTuple[4]
        am.validTo      = databaseTuple[5]

        return am

    #Gibt zurück, ob der Mix outdated ist
    #@param bool True, wenn ja / False, wenn nein
    def isOutdated(self):
        #Wenn aktuelle Zeit größer, gleich der Zeit des Ablaufdatums
        if time.time() >= self.validTo:
            return True
        return False

    #Updated das Attribut "validTo". (void - Funktion)
    def updateValidTo(self):
        #Startzeitpunkt der Validität + Spieldauer
        self.validTo = self.validFrom + self.duration

    #Passt die Attribute "validFrom" und "validTo" mittels neuer "validFrom"-Zeit an. (void - Funktion)
    #@param Int Neuer Unix-Zeitstempel, von wann der Mix an gültig sein soll
    def adjustValidity(self,newValidFrom):
        self.validFrom = newValidFrom
        self.updateValidTo()