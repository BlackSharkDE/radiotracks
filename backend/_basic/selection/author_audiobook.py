########################################################################################################################################################################
#
# Autor & AudioBook
#
########################################################################################################################################################################

import json

from ..base import AudioCreator, AudioCollection, AudioTrack

########################################################################################################################################################################

#Ein Ordner in "media/author/"
class Author(AudioCreator):

    #-- Konstruktor --
    def __init__(self):
        super().__init__()

#Ein Ordner in "media/author/<author_name>/"
class AudioBook(AudioCollection):

    #-- Konstruktor --
    def __init__(self):
        super().__init__()
        self.blurb = "" #Klappentext bzw. Beschreibung des Buchs

    #Überschreibe "Stringrepräsentation"
    def __repr__(self):
        r  = super().__repr__()
        r += "-- AudioBook --\n"
        r += "blurb: " + str(self.blurb) + "\n"
        return r

    #Überschreibe "equals"
    def __eq__(self,other):
        return super().__eq__(self,other) \
        and self.blurb == other.blurb
    
    #Überschreibe "toDict"
    def toDict(self):
        audioBookDict = super().toDict()

        audioBookDict["blurb"] = self.blurb

        return audioBookDict

    #Erstellt ein AudioBook-Objekt aus den Werten, die aus der Datenbank abgefragt wurden.
    #@param Tuple      Das Tuple, welches von der Datenbank zurückgegeben wurde
    #@return AudioBook Ein AudioBook-Objekt
    def fromDBTuple(databaseTuple):
        ac = AudioCollection.fromDBTuple(databaseTuple)

        ab = AudioBook()

        #AudioCollection-Attribute
        ab.id         = ac.id
        ab.name       = ac.name
        ab.path       = ac.path
        ab.mediaPath  = ac.mediaPath
        ab.cover      = ac.cover
        ab.published  = ac.published
        ab.tracks     = AudioTrack.batchCreate(json.loads(databaseTuple[7])) #Nicht in AudioCollection enthalten
        ab.trackCount = ac.trackCount
        ab.duration   = ac.duration

        #AudioBook-Attribute
        ab.blurb = databaseTuple[10]

        return ab