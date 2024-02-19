########################################################################################################################################################################
#
# Kuratierte Playlists
#
# Ein Ordner in "media/curatedplaylist/"
#
########################################################################################################################################################################

import json

from ..base import AudioCollection, AudioTrack

########################################################################################################################################################################

class CuratedPlaylist(AudioCollection):

    #-- Konstruktor --
    def __init__(self):
        super().__init__()
        self.description               = "" #Beschreibung der Playlist
        self.updateInterval            = 0  #Intervall in Sekunden, wie oft geupdated werden soll
        self.lastUpdate                = 0  #Unix-Zeitstempel, wann zuletzt geupdated wurde

    #Überschreibe "Stringrepräsentation"
    def __repr__(self):
        r  = super().__repr__()
        r += "-- CuratedPlaylist --\n"
        r += "description              : " + str(self.description) + "\n"
        r += "updateInterval           : " + str(self.updateInterval) + "\n"
        r += "lastUpdate               : " + str(self.lastUpdate) + "\n"
        return r

    #Überschreibe Gleichheit
    def __eq__(self,other):
        return super().__eq__(self,other) \
        and self.description    == other.description \
        and self.updateInterval == other.updateInterval \
        and self.lastUpdate     == other.lastUpdate

    #Überschreibe "toDict"
    def toDict(self):
        curatedPlaylistDict = super().toDict()

        curatedPlaylistDict["description"]    = self.description
        curatedPlaylistDict["updateInterval"] = self.updateInterval
        curatedPlaylistDict["lastUpdate"]     = self.lastUpdate

        return curatedPlaylistDict

    #Erstellt ein CuratedPlaylist-Objekt aus den Werten, die aus der Datenbank abgefragt wurden.
    #@param Tuple            Das Tuple, welches von der Datenbank zurückgegeben wurde
    #@return CuratedPlaylist Ein CuratedPlaylist-Objekt
    def fromDBTuple(databaseTuple):
        ac = AudioCollection.fromDBTuple(databaseTuple,True)

        cp = CuratedPlaylist()

        #AudioCollection-Attribute
        cp.id         = ac.id
        cp.name       = ac.name
        cp.path       = ac.path
        cp.mediaPath  = ac.mediaPath
        cp.cover      = ac.cover
        cp.published  = ac.published
        cp.tracks     = AudioTrack.batchCreate(json.loads(databaseTuple[6])) #Nicht in AudioCollection enthalten
        cp.trackCount = ac.trackCount
        cp.duration   = ac.duration
        
        #CuratedPlaylist-Attribute
        cp.description    = databaseTuple[9]
        cp.updateInterval = databaseTuple[10]
        cp.lastUpdate     = databaseTuple[11]

        return cp