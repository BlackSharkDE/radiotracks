########################################################################################################################################################################
#
# API-Funktionen für die API-Routen
#
########################################################################################################################################################################

import time
import json

from _basic import RadiotracksDBConnection, AudioFile, AudioTrack
from _basic import Album, AudioBook, Channel, LightChannel, InternetChannel, AdvancedChannel, CuratedPlaylist, PodcastEpisode
from hosting import AdvancedMix

from .broadcastsimulation import broadcastsimulation, searchStarttrackFromPlaylist

########################################################################################################################################################################

#Gibt alle IDs einer aus Tabelle aus
#@param String Name der Tabelle mit den IDs
#@param String Feld in der Tabelle, die die Suche einschränkt (OPTIONAL)
#@param String Wert für Feld (OPTIONAL)
#@return List  Eine Liste mit IDs (Strings) / leere Liste bei Fehler bzw. keinen IDs
def getIds(tableName, whereField = "", whereValue = "", orderBy = "id"):
    rdbc = RadiotracksDBConnection()

    querySql  = "SELECT `id` FROM `" + tableName + "` ORDER BY `" + orderBy + "`"
    queryList = []

    #Solle "whereField" UND "whereValue" angegeben worden sein
    if whereField != "" and whereValue != "":
        querySql = "SELECT `id` FROM `" + tableName + "` WHERE `" + whereField + "` = ? ORDER BY `id`"
        queryList = [whereValue]


    #Alle IDs der übergebenen Tabelle abfragen
    rdbc.databaseCursor.execute(querySql,queryList)
    ids = rdbc.databaseCursor.fetchall()
    ids = [x[0] for x in ids]

    rdbc.closeDatabaseConnection()
    
    return ids

#Gibt ein Tuple aus der Datenbank anhand seiner ID zurück
#@param String Name der Tabelle mit dem Tuple
#@param String ID des Tuple
#@return Tuple Das Tuple bzw. ein leeres Tuple, sollte die ID nicht gefunden werden können
def getTupleFromDB(tupleTableName,tupleId):
    rdbc = RadiotracksDBConnection()

    #Rückgabe-Tuple
    r = ()

    rdbc.databaseCursor.execute("SELECT * FROM `" + tupleTableName + "` WHERE `id` = ?",[tupleId])
    requestedTuple = rdbc.databaseCursor.fetchall()
    if len(requestedTuple) == 1:
        return requestedTuple[0]

    rdbc.closeDatabaseConnection()

    return r

#Gibt ein Objekt aus der Datenbank als Dictionary anhand seiner ID zurück
#@param String Name der Tabelle mit dem Objekt
#@param String ID des Objektes
#@param Class  Ein Klassen-Pointer bzw. die Klasse des Objektes
#@return Dict  Das Objekt als Dictionary bzw. ein leeres Dictionary, sollte das Objekt nicht gefunden werden können
def getObjectFromDB(tableName,objectId,classPointer):
    
    #Tuple aus der Datenbank abfragen
    objectTuple = getTupleFromDB(tableName,objectId)

    #Wenn Tuple gefunden wurde
    if len(objectTuple) > 1:
        #-- Objekt erstellen und als Dictionary zurückgeben --
        requestedObject = classPointer.fromDBTuple(objectTuple)
        return requestedObject.toDict()

    return {}

########################################################################################################################################################################
#-- Routen "/album/" --

#Gibt ein Album anhand seiner ID aus
#@param String Eine Album-ID
#@return Dict  Ein Album-Dictionary / leeres Dictionary, wenn Album nicht gefunden wurde
def getAlbumById(albumId):
    rdbc = RadiotracksDBConnection()

    r = {}

    rdbc.databaseCursor.execute("SELECT * FROM `albums` WHERE `id` = ?",[albumId])
    album = rdbc.databaseCursor.fetchall()
    if len(album) == 1:
        albumObject = Album.fromDBTuple(album[0])

        rdbc.databaseCursor.execute("SELECT `path`,`mediaPath`,`filename`,`duration`,`title` FROM `albumtracks` WHERE `albumid` = ?",[albumId])
        trackTuples = rdbc.databaseCursor.fetchall()
        tracks = list()
        for track in trackTuples:
            tracks.append(AudioTrack.fromDBTuple(track))

        albumObject.tracks = tracks
        r = albumObject.toDict()

        #Zusätzliche Informationen zum Artist anhängen
        rdbc.databaseCursor.execute("SELECT `id`, `name` FROM `artists` WHERE `id` = ?",[album[0][0]])
        artistValues = rdbc.databaseCursor.fetchall()
        artistValues = artistValues[0]
        r.update({"artistId": artistValues[0], "artistName": artistValues[1]})

    rdbc.closeDatabaseConnection()

    return r

#Gibt alle Tracks eines Album anhand seiner ID aus
#@param String Eine Album-ID
#@return List  Eine Liste mit Track-Dictionaries / leere Liste, wenn Album nicht gefunden wurde
def getAlbumTracks(albumId):
    albumDict = getAlbumById(albumId)

    #Wenn das Album Tracks enthält bzw. gefunden wurde
    if len(albumDict.get("tracks",[])) > 0:
        return albumDict["tracks"]
    
    return []

########################################################################################################################################################################
#-- Routen "/audiobook/" --

#Gibt ein AudioBook anhand seiner ID aus
#@param String Eine AudioBook-ID
#@return Dict  Ein AudioBook-Dictionary / leeres Dictionary, wenn AudioBook nicht gefunden wurde
def getAudioBookById(audioBookId):
    rdbc = RadiotracksDBConnection()

    r = {}

    rdbc.databaseCursor.execute("SELECT * FROM `audiobooks` WHERE `id` = ?",[audioBookId])
    audioBook = rdbc.databaseCursor.fetchall()
    if len(audioBook) == 1:
        audioBookObject = AudioBook.fromDBTuple(audioBook[0])

        r = audioBookObject.toDict()

        #Zusätzliche Informationen zum Author anhängen
        rdbc.databaseCursor.execute("SELECT `id`, `name` FROM `authors` WHERE `id` = ?",[audioBook[0][0]])
        authorValues = rdbc.databaseCursor.fetchall()
        authorValues = authorValues[0]
        r.update({"authorId": authorValues[0], "authorName": authorValues[1]})

    rdbc.closeDatabaseConnection()

    return r

#Gibt alle Tracks eines AudioBook anhand seiner ID aus
#@param String Eine AudioBook-ID
#@return List  Eine Liste mit Track-Dictionaries / leere Liste, wenn AudioBook nicht gefunden wurde
def getAudioBookTracks(audioBookId):
    audioBookDict = getAudioBookById(audioBookId)

    #Wenn das AudioBook Tracks enthält bzw. gefunden wurde
    if len(audioBookDict.get("tracks",[])) > 0:
        return audioBookDict["tracks"]
    
    return []

########################################################################################################################################################################
#-- Routen "/channel/" --

#Gibt einen Channel anhand seiner ID aus
#@param String Eine Channel-ID
#@return Dict  Ein Channel-Dictionary / leeres Dictionary, wenn Channel nicht gefunden wurde
def getChannelById(channelId):

    #Channel aus Datenbank abfragen
    channelTuple = getTupleFromDB("channels",channelId)
    
    #Wenn Channel gefunden wurde
    if len(channelTuple) > 1:

        #Channel-Type
        channelType = channelTuple[6]

        #Channel-Objekt
        channel = None

        #Angaben für broadcast-Berechnung
        broadcastList = []
        broadcastInt  = 0

        #Aktuelle Zeit (damit für mehrere Berechnungen der selbe Wert benutzt wird)
        currentTime = int(time.time())

        #Je nachdem, welcher Channel-Type
        if channelType == "LightChannel":
            channel = LightChannel.fromDBTuple(channelTuple)
            for audioFile in channel.tracks:
                broadcastList.append(audioFile)
                broadcastInt += audioFile.duration
        elif channelType == "InternetChannel":
            channel = InternetChannel.fromDBTuple(channelTuple)
        elif channelType == "AdvancedChannel":
            channel = AdvancedChannel.fromDBTuple(channelTuple)
            
            #-- Rufe die AdvancedMix-Tuples aus der Datenbank für den Channel ab --
            rdbc = RadiotracksDBConnection()
            rdbc.databaseCursor.execute("SELECT * FROM `channelmixes` WHERE `advancedChannelId` = ? AND `validTo` > ?",[channel.id,currentTime])
            advancedMixes = rdbc.databaseCursor.fetchall()
            rdbc.closeDatabaseConnection()
            if len(advancedMixes) > 0:
                currentMix = advancedMixes[0]
                currentMix = AdvancedMix.fromDBTuple(currentMix)

                broadcastList = currentMix.tracks
                broadcastInt  = currentMix.validFrom
        
        #Normale Channel-Attribute
        returnChannel           = Channel()
        returnChannel.id        = channel.id
        returnChannel.name      = channel.name
        returnChannel.path      = channel.path
        returnChannel.mediaPath = channel.mediaPath
        returnChannel.cover     = channel.cover
        returnChannel.hostedBy  = channel.hostedBy

        #Rückgabe
        returnDict = returnChannel.toDict()        

        if type(channel) == LightChannel or type(channel) == AdvancedChannel:
            #-- Wenn LightChannel oder AdvancedChannel

            #AudioFile-Objekte in Dictionaries konvertieren
            returnDict.update({"tracks": [x.toDict() for x in broadcastList]})

            #Broadcast errechnen (wenn eine broadcastList verfügbar ist -> betrifft AdvancedChannel ohne aktuelle Mixes)
            broadcast = [0,0] #Standardwerte
            if len(broadcastList) > 0:

                #-- Je nach Channel-Art, wird der Broadcast anders bestimmt --
                if type(channel) == LightChannel:
                    broadcast = broadcastsimulation(broadcastList,broadcastInt)
                elif type(channel) == AdvancedChannel:
                    broadcast = searchStarttrackFromPlaylist(currentTime - broadcastInt,broadcastList)

            returnDict.update({"broadcast": {"index": broadcast[0], "start": broadcast[1]}})
        else:
            #-- Wenn InternetChannel --

            #Die Tracks sind ein angepasstes AudioFile-Objekt, welches die Stream-URL beinhaltet
            customAudioFile = AudioFile()
            customAudioFile.mediaPath =  channel.streamUrl
            customAudioFile.duration  = -1
            returnDict.update({"tracks": [customAudioFile.toDict()]})

            #"broadcast" wird leer angegeben
            returnDict.update({"broadcast": {}})

        return returnDict
    
    #Channel nicht gefunden
    return {}

#Gibt den vorherigen Channel zurück
#@param String Eine Channel-ID (der aktuelle)
#@return Dict  Ein Channel-Dictionary / leeres Dictionary, wenn Channel nicht gefunden wurde
def getPreviousChannel(channelId):

    #Channel-IDs nach Channel-Namen sortiert
    channelIds = getIds("channels","","","name")

    try:
        channelIndex = channelIds.index(channelId)
    except:
        #Channel-ID nicht in Liste
        return {}

    #Vorherigen Channel bestimmen
    previousIndex = channelIndex - 1
    if previousIndex < 0:
        previousIndex = len(channelIds) - 1

    return getChannelById(channelIds[previousIndex])

#Gibt den nächsten Channel zurück
#@param String Eine Channel-ID (der aktuelle)
#@return Dict  Ein Channel-Dictionary / leeres Dictionary, wenn Channel nicht gefunden wurde
def getNextChannel(channelId):
    
    #Channel-IDs nach Channel-Namen sortiert
    channelIds = getIds("channels","","","name")

    try:
        channelIndex = channelIds.index(channelId)
    except:
        #Channel-ID nicht in Liste
        return {}

    #Nächsten Channel bestimmen
    nextIndex = channelIndex + 1
    if nextIndex > len(channelIds) - 1:
        nextIndex = 0

    return getChannelById(channelIds[nextIndex])

########################################################################################################################################################################
#-- Routen "/curatedplaylist/"

#Gibt alle Tracks einer CuratedPlaylist anhand ihrer ID aus
#@param String Eine CuratedPlaylist-ID
#@return List  Eine Liste mit Track-Dictionaries / leere Liste, wenn CuratedPlaylist nicht gefunden wurde
def getCuratedPlaylistTracks(curatedPlaylistId):
    curatedPlaylist = getTupleFromDB("curatedplaylists",curatedPlaylistId)

    #Wenn die CuratedPlaylist gefunden wurde
    if len(curatedPlaylist) > 0:

        #Erstelle Objekt von Tuple
        curatedPlaylist = CuratedPlaylist.fromDBTuple(curatedPlaylist)

        #Wenn Tracks vorhanden sind
        if len(curatedPlaylist.tracks) > 0:
            rdbc = RadiotracksDBConnection()

            #Liste mit angepassten Track-Dictionaries
            newTracksList = []

            #Jeden Track erweitern
            for track in curatedPlaylist.tracks:

                #Extra Werte, die dem Track angehangen werden sollen
                extraValues = {"artistName" : "", "albumName": "", "cover" : ""}

                #Album-ID für weitere Abfrage besorgen
                rdbc.databaseCursor.execute("SELECT `albumid` FROM `albumtracks` WHERE `mediaPath` = ?",[track.mediaPath])
                albumId = rdbc.databaseCursor.fetchall()
                if len(albumId) == 1:
                    albumId = albumId[0][0]

                    #Herausfinden der Artist-ID für weitere Abfrage und Album-Name & Album-Cover für Endresultat
                    rdbc.databaseCursor.execute("SELECT `artistid`,`name`,`cover` FROM `albums` WHERE `id` = ?",[albumId])
                    albumValues = rdbc.databaseCursor.fetchall()
                    if len(albumValues) == 1:
                        albumValues = albumValues[0]

                        #Herausgefundene Werte speichen
                        extraValues["albumName"] = albumValues[1]
                        extraValues["cover"]     = albumValues[2]

                        #Artist-Name anhand der ID herausfinden
                        rdbc.databaseCursor.execute("SELECT `name` FROM `artists` WHERE `id` = ?",[albumValues[0]])
                        artistName = rdbc.databaseCursor.fetchall()
                        if len(artistName) == 1:
                            artistName = artistName[0][0]

                            #Herausgefundenen Wert speichen
                            extraValues["artistName"] = artistName

                            #Modifiziertes Track-Dictionary erstellen
                            newTrackDict = track.toDict()
                            newTrackDict.update(extraValues)

                            #Modifiziertes Track-Dictionary speichen
                            newTracksList.append(newTrackDict)

            rdbc.closeDatabaseConnection()

            return newTracksList

    #CuratedPlaylist nicht gefunden
    return []

########################################################################################################################################################################
#-- Routen "/podcast/" --

#Gibt alle Episoden eines Podcasts anhand seiner ID aus
#@param String Eine Podcast-ID
#@return List  Eine Liste mit PodcastEpisode-Dictionaries / leeres Liste, wenn Podcast nicht gefunden wurde
def getPodcastEpisodes(podcastId):
    rdbc = RadiotracksDBConnection()

    r = {}

    rdbc.databaseCursor.execute("SELECT * FROM `podcastepisodes` WHERE `podcastid` = ?",[podcastId])
    podcastEpisodes = rdbc.databaseCursor.fetchall()
    if len(podcastEpisodes) > 0:
        
        episodesList = list()
        for episode in podcastEpisodes:
            episodesList.append(PodcastEpisode.fromDBTuple(episode).toDict())

        r = episodesList

    rdbc.closeDatabaseConnection()

    return r