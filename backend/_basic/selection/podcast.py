########################################################################################################################################################################
#
# Podcasts
#
# Ein Ordner in "media/podcast/"
#
########################################################################################################################################################################

from ..base import BasicType, AudioFile

########################################################################################################################################################################

#Der Podcast
class Podcast(BasicType):

    #-- Konstruktor --
    def __init__(self):
        super().__init__()
        self.description     = ""     #Beschreibung des Podcasts
        self.publisher       = ""     #Herausgeber des Podcasts
        self.episodes        = list() #Liste mit "PodcastEpisode"-Objekten (die Podcast-Episoden)
        self.episodeCount    = 0      #Wie viele Episoden der Podcast besitzt

    #Überschreibe "Stringrepräsentation"
    def __repr__(self):
        r  = super().__repr__()
        r += "-- Podcast --\n"
        r += "description : " + str(self.description) + "\n"
        r += "publisher   : " + str(self.publisher) + "\n"
        r += "episodes    : " + str(self.episodes) + "\n"
        r += "episodeCount: " + str(self.episodeCount) + "\n"
        return r

    #Überschreibe Gleichheit
    def __eq__(self,other):
        return super().__eq__(self,other) \
        and self.description  == other.description \
        and self.publisher    == other.publisher \
        and self.episodes     == other.episodes \
        and self.episodeCount == other.episodeCount

    #Überschreibe "toDict"
    def toDict(self):
        podcastDict = super().toDict()
        
        podcastDict["description"]  = self.description
        podcastDict["publisher"]    = self.publisher
        podcastDict["episodes"]     = list()
        for episode in self.episodes:
            podcastDict["episodes"].append(episode.toDict())
        podcastDict["episodeCount"] = self.episodeCount
        
        return podcastDict

    #Erstellt ein Podcast-Objekt aus den Werten, die aus der Datenbank abgefragt wurden.
    #@param Tuple    Das Tuple, welches von der Datenbank zurückgegeben wurde
    #@return Podcast Ein Podcast-Objekt
    def fromDBTuple(databaseTuple):
        b = BasicType.fromDBTuple(databaseTuple[0:5])

        podcast = Podcast()

        #BasicType-Attribute übernehmen
        podcast.id        = b.id
        podcast.name      = b.name
        podcast.path      = b.path
        podcast.mediaPath = b.mediaPath
        podcast.cover     = b.cover

        #Podcast-Attribute
        podcast.description  = databaseTuple[5]
        podcast.publisher    = databaseTuple[6]
        #"episodes" muss anders zugewiesen werden
        podcast.episodeCount = databaseTuple[7]

        return podcast

#Die Podcast-Episode
class PodcastEpisode(AudioFile):

    #-- Konstruktor --
    def __init__(self):
        super().__init__()
        self.title       = "" #Name der Episode (aus JSON-Datei)
        self.description = "" #Beschreibung der Episode (aus JSON-Datei)

    #Überschreibe "Stringrepräsentation"
    def __repr__(self):
        r = super().__repr__()
        r += "-- PodcastEpisode --\n"
        r += "title      : " + str(self.title) + "\n"
        r += "description: " + str(self.description) + "\n"
        return r

    #Überschreibe "equals"
    def __eq__(self,other):
        return super().__eq__(self,other) \
        and self.title       == other.title \
        and self.description == other.description

    #Überschreibe "toDict"
    def toDict(self):
        d = super().toDict()
        d["title"]       = self.title
        d["description"] = self.description
        return d

    #Erstellt ein Podcast-Objekt aus den Werten, die aus der Datenbank abgefragt wurden.
    #@param Tuple    Das Tuple, welches von der Datenbank zurückgegeben wurde
    #@return Podcast Ein Podcast-Objekt
    def fromDBTuple(databaseTuple):
        podcastEpisode = PodcastEpisode()

        #AudioFile-Attribute
        podcastEpisode.path      = databaseTuple[1]
        podcastEpisode.mediaPath = databaseTuple[2]
        podcastEpisode.filename  = databaseTuple[3]
        podcastEpisode.duration  = databaseTuple[4]

        #PodcastEpisode-Attribute
        podcastEpisode.title       = databaseTuple[5]
        podcastEpisode.description = databaseTuple[6]

        return podcastEpisode