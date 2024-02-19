########################################################################################################################################################################
#
# Channels
#
# Ein Ordner in "media/channel/channels/"
#
########################################################################################################################################################################

import json
import datetime

import jfiles

from ..base import BasicType, AudioFile

########################################################################################################################################################################

#Diese Klasse ist als abstrakt zu verstehen, muss also geerbt und erweitert werden.
class Channel(BasicType):

    #-- Konstruktor --
    def __init__(self):
        super().__init__()
        self.hostedBy = ""     #String mit kommaseparierten Namen der Personen, die den Channel hosten
        self.tags     = list() #Liste mit Strings, die den Channel beschreiben
    
    #Überschreibe "Stringrepräsentation"
    def __repr__(self):
        r  = super().__repr__()
        r += "-- Channel --\n"
        r += "hostedBy: " + str(self.hostedBy) + "\n"
        r += "tags    : " + str(self.tags) + "\n"
        return r
    
    #Überschreibe "equals"
    def __eq__(self,other):
        return super().__eq__(self,other) \
        and self.hostedBy == other.hostedBy \
        and self.tags     == other.tags
    
    #Überschreibe "toDict"
    def toDict(self):
        channelDict = super().toDict()

        channelDict["hostedBy"] = self.hostedBy
        channelDict["tags"]     = self.tags

        return channelDict

    #Erstellt ein Channel-Objekt aus den Werten, die aus der Datenbank abgefragt wurden.
    #@param Tuple    Das Tuple, welches von der Datenbank zurückgegeben wurde
    #@return Channel Ein Channel-Objekt
    def fromDBTuple(databaseTuple):
        c = Channel()

        #Channel-Attribute
        c.id        = databaseTuple[0]
        c.name      = databaseTuple[1]
        c.path      = databaseTuple[2]
        c.mediaPath = databaseTuple[3]
        c.cover     = databaseTuple[4]
        c.hostedBy  = databaseTuple[5]
        c.tags      = c.tags #Werden nie von der DB abgefragt

        return c

class LightChannel(Channel):

    #-- Konstruktor --
    def __init__(self):
        super().__init__()
        self.tracks = list() #Musiktracks (Liste mit "AudioFile"-Objekten)
    
    #Überschreibe "Stringrepräsentation"
    def __repr__(self):
        r  = super().__repr__()
        r += "-- LightChannel --\n"
        r += "tracks: " + str(self.tracks) + "\n"
        return r

    #Überschreibe "equals"
    def __eq__(self,other):
        return super().__eq__(self,other) \
        and self.tracks == other.tracks

    #Überschreibe "toDict"
    def toDict(self):
        lightChannelDict = super().toDict()

        lightChannelDict["tracks"] = [x.toDict() for x in self.tracks]

        return lightChannelDict

    #Erstellt ein LightChannel-Objekt aus den Werten, die aus der Datenbank abgefragt wurden.
    #@param Tuple         Das Tuple, welches von der Datenbank zurückgegeben wurde
    #@return LightChannel Ein LightChannel-Objekt
    def fromDBTuple(databaseTuple):
        c = Channel.fromDBTuple(databaseTuple)

        lc = LightChannel()
        
        #Channel-Attribute
        lc.id        = c.id
        lc.name      = c.name
        lc.path      = c.path
        lc.mediaPath = c.mediaPath
        lc.cover     = c.cover
        lc.hostedBy  = c.hostedBy
        lc.tags      = c.tags

        #LightChannel-Attribute
        lc.tracks = AudioFile.batchCreate(json.loads(databaseTuple[16]))

        return lc

class InternetChannel(Channel):

    #-- Konstruktor --
    def __init__(self):
        super().__init__()
        self.streamUrl = "" #URL zum Internet-Stream (aktuell nur MP3-Streams / was die Browser unterstützen)
    
    #Überschreibe "Stringrepräsentation"
    def __repr__(self):
        r  = super().__repr__()
        r += "-- InternetChannel --\n"
        r += "streamUrl: " + str(self.streamUrl) + "\n"
        return r
    
    #Überschreibe "equals"
    def __eq__(self,other):
        return super().__eq__(self,other) \
        and self.streamUrl == other.streamUrl
    
    #Überschreibe "toDict"
    def toDict(self):
        internetChannelDict = super().toDict()

        internetChannelDict["streamUrl"] = self.streamUrl

        return internetChannelDict

    #Erstellt ein InternetChannel-Objekt aus den Werten, die aus der Datenbank abgefragt wurden.
    #@param Tuple            Das Tuple, welches von der Datenbank zurückgegeben wurde
    #@return InternetChannel Ein InternetChannel-Objekt
    def fromDBTuple(databaseTuple):
        c = Channel.fromDBTuple(databaseTuple)

        ic = InternetChannel()
        
        #Channel-Attribute
        ic.id        = c.id
        ic.name      = c.name
        ic.path      = c.path
        ic.mediaPath = c.mediaPath
        ic.cover     = c.cover
        ic.hostedBy  = c.hostedBy
        ic.tags      = c.tags

        #InternetChannel-Attribute
        ic.streamUrl = databaseTuple[7]

        return ic

class AdvancedChannel(Channel):

    #-- Konstruktor --
    def __init__(self):
        super().__init__()
        self.advertsFolder   = ""     #Ordnername in "media/channel/adverts"
        self.newsFolder      = ""     #Ordnername in "media/channel/news"
        self.weatherFolder   = ""     #Ordnername in "media/channel/weather"
        self.idTracks        = list() #Channel-Intros (die den Channel ansagen) (Liste mit "AudioFile"-Objekten)
        self.introTracks     = list() #Musik-Track-Ansagen und Abmoderationen der einzelnen Tracks (Liste mit "AudioFile"-Objekten)
        self.monologueTracks = list() #Monologe / Gespräche der Moderatoren (Liste mit "AudioFile"-Objekten)
        self.timeTracks      = {"morning": list(), "afternoon": list(), "evening": list(), "night": list()} #Zeitansagen (Morning / Afternoon / Evening / Night)
        self.toTracks        = {"adverts": list(), "news": list(), "weather": list()} #Überleitungstracks (News / Werbung / Wetter)
        self.tracks          = list() #Musiktracks (Liste mit "AudioFile"-Objekten)

    #Überschreibe "Stringrepräsentation"
    def __repr__(self):
        r  = super().__repr__()
        r += "-- AdvancedChannel --\n"
        r += "advertsFolder  : " + str(self.advertsFolder) + "\n"
        r += "newsFolder     : " + str(self.newsFolder) + "\n"
        r += "weatherFolder  : " + str(self.weatherFolder) + "\n"
        r += "idTracks       : " + str(self.idTracks) + "\n"
        r += "introTracks    : " + str(self.introTracks) + "\n"
        r += "monologueTracks: " + str(self.monologueTracks) + "\n"
        r += "timeTracks     : " + str(self.timeTracks) + "\n"
        r += "toTracks       : " + str(self.toTracks) + "\n"
        r += "tracks         : " + str(self.tracks) + "\n"
        return r

    #Überschreibe "equals"
    def __eq__(self,other):
        return super().__eq__(self,other) \
        and self.advertsFolder   == other.advertsFolder \
        and self.newsFolder      == other.newsFolder \
        and self.weatherFolder   == other.weatherFolder \
        and self.idTracks        == other.idTracks \
        and self.introTracks     == other.introTracks \
        and self.monologueTracks == other.monologueTracks \
        and self.timeTracks      == other.timeTracks \
        and self.toTracks        == other.toTracks \
        and self.tracks          == other.tracks

    #Überschreibe "toDict"
    def toDict(self):
        advancedChannelDict = super().toDict()

        advancedChannelDict["advertsFolder"]   = self.advertsFolder
        advancedChannelDict["newsFolder"]      = self.newsFolder
        advancedChannelDict["weatherFolder"]   = self.weatherFolder
        advancedChannelDict["idTracks"]        = [x.toDict() for x in self.idTracks]
        advancedChannelDict["introTracks"]     = [x.toDict() for x in self.introTracks]
        advancedChannelDict["monologueTracks"] = [x.toDict() for x in self.monologueTracks]
        advancedChannelDict["timeTracks"]      = {
            'morning'  : [x.toDict() for x in self.timeTracks["morning"]],
            'afternoon': [x.toDict() for x in self.timeTracks["afternoon"]],
            'evening'  : [x.toDict() for x in self.timeTracks["evening"]],
            'night'    : [x.toDict() for x in self.timeTracks["night"]]
        }
        advancedChannelDict["toTracks"]        = {
            'adverts': [x.toDict() for x in self.toTracks["adverts"]],
            'news'   : [x.toDict() for x in self.toTracks["news"]],
            'weather': [x.toDict() for x in self.toTracks["weather"]]
        }
        advancedChannelDict["tracks"]          = [x.toDict() for x in self.tracks]

        return advancedChannelDict

    #Erstellt ein AdvancedChannel-Objekt aus den Werten, die aus der Datenbank abgefragt wurden.
    #@param Tuple            Das Tuple, welches von der Datenbank zurückgegeben wurde
    #@return AdvancedChannel Ein AdvancedChannel-Objekt
    def fromDBTuple(databaseTuple):
        c = Channel.fromDBTuple(databaseTuple)

        ac = AdvancedChannel()
        
        #Channel-Attribute
        ac.id        = c.id
        ac.name      = c.name
        ac.path      = c.path
        ac.mediaPath = c.mediaPath
        ac.cover     = c.cover
        ac.hostedBy  = c.hostedBy
        ac.tags      = c.tags

        #AdvancedChannel-Attribute
        ac.advertsFolder   = databaseTuple[8]
        ac.newsFolder      = databaseTuple[9]
        ac.weatherFolder   = databaseTuple[10]
        ac.idTracks        = AudioFile.batchCreate(json.loads(databaseTuple[11]))
        ac.introTracks     = AudioFile.batchCreate(json.loads(databaseTuple[12]))
        ac.monologueTracks = AudioFile.batchCreate(json.loads(databaseTuple[13]))

        timeTracks = json.loads(databaseTuple[14])
        ac.timeTracks["morning"]   = AudioFile.batchCreate(timeTracks["morning"])
        ac.timeTracks["afternoon"] = AudioFile.batchCreate(timeTracks["afternoon"])
        ac.timeTracks["evening"]   = AudioFile.batchCreate(timeTracks["evening"])
        ac.timeTracks["night"]     = AudioFile.batchCreate(timeTracks["night"])

        toTracks = json.loads(databaseTuple[15])
        ac.toTracks["adverts"] = AudioFile.batchCreate(toTracks["adverts"])
        ac.toTracks["news"]    = AudioFile.batchCreate(toTracks["news"])
        ac.toTracks["weather"] = AudioFile.batchCreate(toTracks["weather"])

        ac.tracks     = AudioFile.batchCreate(json.loads(databaseTuple[16]))

        return ac

    #Gibt alle möglichen Intros für einen Musiktrack zurück
    #-> ACHTUNG: Rückgabe-Liste kann leer sein
    #@param AudioFile Ein AudioFile-Objekt aus der "tracks"-Eigenschaft
    #@return List     Liste mit AudioFile-Objekten
    def getIntrosForTrack(self,track):
        
        #Rückgabe
        result = list()

        #Track-Dateiname ohne Dateiendung
        trackName = jfiles.getFilenameNoExtension(track.filename)

        #Intros des Channel durchsuchen
        for intro in self.introTracks:

            #Name des Intro-Dateinamen ohne Dateiendung
            introName = jfiles.getFilenameNoExtension(intro.filename)

            #Wenn der Trackname im Intronamen vorkommt UND "_(ended)" nicht enthalten ist
            if introName.find(trackName) > -1 and introName.find("_(ended)") == -1:
                result.append(intro)
        
        return result

    #Gibt alle möglichen Outros für einen Musiktrack zurück (Ein Intro, das zusätzlich den String "_(ended)" enthält)
    #-> ACHTUNG: Rückgabe-Liste kann leer sein
    #@param AudioFile Ein AudioFile-Objekt aus der "tracks"-Eigenschaft
    #@return List     Liste mit AudioFile-Objekten
    def getOutrosForTrack(self,track):

        #Rückgabe
        result = list()

        #Track-Dateiname ohne Dateiendung
        trackName = jfiles.getFilenameNoExtension(track.filename)

        #Intros des Channel durchsuchen (werden hier als Outros behandelt)
        for outro in self.introTracks:

            #Name des Intro-Dateinamen ohne Dateiendung
            outroName = jfiles.getFilenameNoExtension(outro.filename)

            #Wenn der Trackname im Intronamen vorkommt UND "_(ended)" enthalten ist
            if outroName.find(trackName) > -1 and outroName.find("_(ended)") > -1:
                result.append(outro)
            
        return result

    #Gibt der Uhrzeit entsprechend die Tracks aus "timeTracks" zurück
    #@param int  Offset (kann positiv/negativ sein) um das die Uhrzeit verschoben werden soll in Sekunden (OPTIONAL)
    #-> ACHTUNG: Rückgabe-Liste kann leer sein
    #@return List Eine Liste aus dem "timeTracks"-Dictionary
    def getTimeTracks(self,offsetSeconds = 0):
        
        #Aktuelle Stunde
        time = datetime.datetime.now()
        time = time + datetime.timedelta(seconds=offsetSeconds)
        hour = time.hour

        #Tag wird so eingeteilt:
        #- 0, 1, 2, 3, 4, 5  -> Night
        #- 6, 7, 8, 9,10,11  -> Morning
        #- 12,13,14,15,16,17 -> Afternoon
        #- 18,19,20,21,22,23 -> Evening

        if hour >= 0 and hour <= 5:
            return self.timeTracks["night"]
        elif hour >= 6 and hour <= 11:
            return self.timeTracks["morning"]
        elif hour >= 12 and hour <= 17:
            return self.timeTracks["afternoon"]
        elif hour >= 18 and hour <= 23:
            return self.timeTracks["evening"]