########################################################################################################################################################################
#
# Die API-App (Flask)
#
########################################################################################################################################################################

from flask import Flask, Response

import json
import multiprocessing

from _basic import RadiotracksLog, RadiotracksDBConnection, Artist, Author, CuratedPlaylist, Podcast, PodcastEpisode
from _basic import getSetting, getRandomness, getRandomItemFromList, indexExistsInList

from .functions import getIds, getObjectFromDB
from .functions import getAlbumById, getAlbumTracks
from .functions import getAudioBookById, getAudioBookTracks
from .functions import getChannelById, getPreviousChannel, getNextChannel
from .functions import getCuratedPlaylistTracks
from .functions import getPodcastEpisodes

########################################################################################################################################################################
#-- Allgemeines --

#Variable mit der API-App
app = Flask(__name__)

########################################################################################################################################################################
#-- Steuerung der API (eigener Python-Prozess) --

#-- Startmethoden (Funktionen für Multiprocessing) --

#Startet die API mittels Waitress (production). (void - Funktion)
def startApi_Waitress():
    global app #Globale Variable "app"

    #Datenbankeinstellungen nochmal laden (da extra Prozess)
    RadiotracksDBConnection.loadSettings()

    #Einstellungen abrufen
    apiSettings = getSetting("api")

    #Für hinter Proxy bzw. wenn Waitress hinter einem Proxy ist (= Reverse Proxy)
    if apiSettings["usesReverseProxy"]:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    RadiotracksLog.log("RadiotracksAPI","Starting (production) on " + str(apiSettings["host"]) + ":" + str(apiSettings["port"]))

    #Waitress importieren und starten
    from waitress import serve
    serve(
        app,
        host       = apiSettings["host"],
        port       = apiSettings["port"],
        url_scheme = apiSettings["reverseProxyUrlScheme"],
        threads    = apiSettings["waitressThreads"]
    )

#Startet die API mittels Flask-Webserver (development). (void - Funktion)
def startApi_Flask():
    global app #Globale Variable "app"

    #Datenbankeinstellungen nochmal laden (da extra Prozess)
    RadiotracksDBConnection.loadSettings()
    
    #Einstellungen abrufen
    apiSettings = getSetting("api")

    RadiotracksLog.log("RadiotracksAPI","Starting (development) on " + str(apiSettings["host"]) + ":" + str(apiSettings["port"]))

    #Flask-Webserver starten
    app.run(
        host         = apiSettings["host"], 
        port         = apiSettings["port"],
        debug        = True, #Nur Entwicklungszwecke!
        threaded     = True, #Damit man mehrere Clients gleichzeitig bedienen kann
        use_reloader = False #Ob das automatische Erkennen von Änderungen im Quellcode erkannt werden soll
    )

#Steuerungsklasse (statisch)
class RadiotracksAPI:

    #API-Prozess (Webserver)
    apiProcess = None

    #Startet / Stoppt die API. (void - Funktion)
    def startStopApi():
        if RadiotracksAPI.apiProcess is None:
            RadiotracksAPI.startApi()
        else:
            RadiotracksAPI.stopApi()

    #Startet die API. (void - Funktion)
    def startApi():
        if RadiotracksAPI.apiProcess is None:
            functionPointer = None

            #Funktions-Pointer heraussuchen
            if(getSetting("api")["production"]):
                functionPointer = startApi_Waitress
            else:
                functionPointer = startApi_Flask

            #Prozess erstellen und starten
            RadiotracksAPI.apiProcess = multiprocessing.Process(target=functionPointer)
            RadiotracksAPI.apiProcess.start()

    #Stoppt die API. (void - Funktion)
    def stopApi():
        if RadiotracksAPI.apiProcess is not None:
            RadiotracksAPI.apiProcess.terminate()
            RadiotracksAPI.apiProcess = None
            RadiotracksLog.log("RadiotracksAPI","Stopped")

########################################################################################################################################################################
#-- Routen --

#Gibt eine Antwort für den Server zurück
#@param - Variabel bzw. die Rückgabe der jeweigen Routen-Funktion, die als JSON ausgegeben werden soll
def getResponse(respsonseContent):

    #Antwort in JSON umwandeln
    respsonseContent = json.dumps(respsonseContent)

    #Response-Objekt
    response = Response(respsonseContent,mimetype="application/json")

    #CORS
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")

    return response

@app.route("/")
def index():
    return getResponse("Radiotracks-API is running!")

@app.errorhandler(404)
def not_found(error):
    return getResponse("Could not find your route!")

########################################################################################################################################################################
#-- Außergewöhnliche Routen --

@app.route("/spotlights")
def spotlights():

    #Rückgabe-Dict
    r = {
        "artists"  : [],
        "authors"  : [],
        "channels" : [],
        "playlists": [],
        "podcasts" : []
    }

    #Pickt zufällig IDs heraus
    #@param List  Liste mit IDs
    #@return List Liste mit IDs / leere Liste, wenn keine IDs
    def getRandomIds(listOfIds):
        l = []
        for i in range(getRandomness(0,6)):
            t = getRandomItemFromList(listOfIds,True)
            if t is not None:
                l.append(t)
        return l

    #Zwischenspeichern von IDs
    r["artists"]   = getRandomIds(artist_ids().get_json())
    r["authors"]   = getRandomIds(author_ids().get_json())
    r["channels"]  = getRandomIds(channel_ids().get_json())
    r["playlists"] = getRandomIds(curatedplaylist_ids().get_json())
    r["podcasts"]  = getRandomIds(podcast_ids().get_json())

    #IDs durch entprechende Dictionaries ersetzen
    r["artists"]   = [artist_id(x).get_json() for x in r["artists"]]
    r["authors"]   = [author_id(x).get_json() for x in r["authors"]]
    r["channels"]  = [channel_id(x).get_json() for x in r["channels"]]
    r["playlists"] = [curatedplaylist_id(x).get_json() for x in r["playlists"]]
    r["podcasts"]  = [podcast_id(x).get_json() for x in r["podcasts"]]

    return getResponse(r)

@app.route("/search/<string:term>")
def search(term):

    r = {
        #Begriff mit zurückgeben (für Debug)
        "term": term,

        #Gefundenes im Angebot
        "artists"         : [],
        "albums"          : [],
        "authors"         : [],
        "audiobooks"      : [],
        "channels"        : [],
        "curatedplaylists": [],
        "podcasts"        : [],

        #Album-Tracks, Hörbuch-Tracks, Podcast-Episoden
        "tracks" : []
    }

    #Suchbegriff aufbereiten
    term  = term.strip()    #Leerzeichen am Anfang und Ende entfernen
    terms = term.split(" ") #Bei den Leerzeichen splitten
    terms = [x for x in terms if len(x) > 0]       #Liste mit Suchbegriffen (Begriff muss Länge > 0 haben)
    terms = ["%" + x.strip() + "%" for x in terms] #Terme bauen ("%" + term + "%")
    termsLen = len(terms) #Anzahl der Terme

    #Datenbanverbindung
    rdbc = RadiotracksDBConnection()

    #Erstellt den WHERE-Abschnitt in den SQL-Queries, der mittels LIKE vergleicht
    #@param String  Wie die Spalte heißt, welche mittels LIKE verglichen werden soll
    #@return String WHERE-Abteil nach dem Muster "(`spalte` LIKE ? AND `spalte` LIKE ?)"
    #               -> Die ?-Platzhalter werden ja durch "terms"-Listeneinträge ersetzt...
    def getLikeWhere(likeComparisonField):
        likeWhere = "("
        for i in range(termsLen):
            if i == 0:
                #Beim erstem Item entfällt das "AND"
                likeWhere += "`" + likeComparisonField + "` LIKE ?"
            else:
                #Weitere Items mit "AND" anknüpfen
                likeWhere += " AND `" + likeComparisonField + "` LIKE ?"
        likeWhere += ")"
        return likeWhere

    #Durchsucht eine Tabelle mittels LIKE-Operator
    #@param String   Name der Tabelle, in der gesucht werden soll
    #@param List     Ziel-Liste, in die Ergebnisse gespeichert werden sollen
    #@param Function Funktion, die zum Konvertieren der ID in ein Dict benutzt werden soll
    #@param String   Name der ID-Spalte in der Tabelle (OPTIONAL)
    #@param String   Name des Feldes, anhand das LIKE ausgeführt wird (OPTIONAL)
    def searchDatabase(table,targetList,funcToConvert,idName = "id",whereField = "name"):

        #Wenn Terme angegeben wurden (verhindere leere Queries)
        if termsLen > 0:

            #Die SQL-Query bauen
            query = "SELECT `" + idName + "` FROM `" + table + "` WHERE " + getLikeWhere(whereField)

            rdbc.databaseCursor.execute(query,terms)
            ids = rdbc.databaseCursor.fetchall()
            if len(ids):
                for id in ids:
                    objDict = funcToConvert(id[0],True)
                    if objDict not in targetList:
                        targetList.append(objDict)

    searchDatabase("artists",r["artists"],artist_id)
    searchDatabase("albums",r["albums"],album_id)
    searchDatabase("albums",r["albums"],album_id,"id","published")

    searchDatabase("authors",r["authors"],author_id)
    searchDatabase("audiobooks",r["audiobooks"],audiobook_id)
    searchDatabase("audiobooks",r["audiobooks"],audiobook_id,"id","blurb")

    searchDatabase("channels",r["channels"],channel_id)
    searchDatabase("channels",r["channels"],channel_id,"id","hostedBy")
    searchDatabase("channeltags",r["channels"],channel_id,"channelid","tag")

    searchDatabase("curatedplaylists",r["curatedplaylists"],curatedplaylist_id)
    searchDatabase("curatedplaylists",r["curatedplaylists"],curatedplaylist_id,"id","published")

    searchDatabase("podcasts",r["podcasts"],podcast_id)
    searchDatabase("podcasts",r["podcasts"],podcast_id,"id","description")

    #Gibt den Index eines Track anhand seines `filename`-Attributs aus
    #@param String  Ein Dateiname nach dem Muster "Zahl - Irgendein Name_mit $ egal - was.Dateiendung" ist
    #@return String Datei Index (Zahl - 1) / -1 wenn nicht gefunden
    def getTrackIndex(aFilename):
        number = aFilename.find("-")

        if number > -1:
            index = aFilename[0:number].strip()
            return int(index) - 1
        
        return -1

    #Wenn Terme angegeben wurden (verhindere leere Queries)
    if termsLen > 0:

        #Frage Album-Tracks ab
        rdbc.databaseCursor.execute("SELECT `albumid`, `filename` FROM `albumtracks` WHERE " + getLikeWhere("title"),terms)
        albumTracks = rdbc.databaseCursor.fetchall()
        if len(albumTracks) > 0:
            for albumTrack in albumTracks:
                #Album-ID zwischenspeichern
                albumId = albumTrack[0]

                #Album-Dict besorgen
                albumDict = getAlbumById(albumId)

                #Track aus Album heraussuchen
                trackIndex = getTrackIndex(albumTrack[1])    #Index-Zahl des Tracks
                
                #Track nur dem Resultat hinzufügen, wenn "trackIndex" valide
                if indexExistsInList(albumDict["tracks"],trackIndex):
                    track = albumDict["tracks"][trackIndex] #Der Album-Track

                    #Zusätzliche Informationen für das Frontend, die normalerweise nicht im Track enthalten sind, an den Track anhängen
                    track["artist"]  = albumDict["artistName"]
                    track["album"]   = albumDict["name"]
                    track["albumId"] = albumDict["id"]
                    track["cover"]   = albumDict["cover"]

                    r["tracks"].append(track)
                else:
                    RadiotracksLog.log("RadiotracksAPI","search: Invalid index " + str(trackIndex) + " in 'tracks'-list of Album " + albumDict["id"] + " -> Can't append to result!")

    #Wenn Terme angegeben wurden (verhindere leere Queries)
    if termsLen > 0:

        #Frage Podcast-Episoden ab
        podcastEpisodes = []

        rdbc.databaseCursor.execute("SELECT * FROM `podcastepisodes` WHERE " + getLikeWhere("title"),terms) #Durchsuche "title"
        podcastEpisodes += rdbc.databaseCursor.fetchall()
        
        rdbc.databaseCursor.execute("SELECT * FROM `podcastepisodes` WHERE " + getLikeWhere("description"),terms) #Durchsuche "description"
        podcastEpisodes += rdbc.databaseCursor.fetchall()
        podcastEpisodes = list(set(podcastEpisodes)) #ggf. doppelte Einträge entfernen
        for podcastEpisode in podcastEpisodes:

            #Dict vom Podcast
            podcastDict = podcast_id(podcastEpisode[0],True)

            #Zusätzliche Informationen für das Frontend, die normalerweise nicht im PodcastEpisode enthalten sind, an die PodcastEpisode anhängen
            podcastEpisodeDict = PodcastEpisode.fromDBTuple(podcastEpisode).toDict()
            podcastEpisodeDict["artist"]    = podcastEpisodeDict.pop("description") #Ersetze den Key "description"
            podcastEpisodeDict["album"]     = podcastDict["name"]
            podcastEpisodeDict["podcastId"] = podcastDict["id"]
            podcastEpisodeDict["cover"]     = podcastDict["cover"]

            r["tracks"].append(podcastEpisodeDict)

    rdbc.closeDatabaseConnection()

    return getResponse(r)

########################################################################################################################################################################
#-- Routen "/artist/" --

@app.route("/artist/ids")
def artist_ids():
    return getResponse(getIds("artists"))

@app.route("/artist/id/<string:id>")
def artist_id(id,internal = False):
    artistDict = getObjectFromDB("artists",id,Artist)
    if internal: return artistDict
    return getResponse(artistDict)

@app.route("/artist/all")
def artist_all():
    artistIds = getIds("artists")
    r = []
    for artistId in artistIds:
        r.append(artist_id(artistId,True))
    return getResponse(r)

@app.route("/artist/albumids/<string:id>")
def artist_albumids(id):
    return getResponse(getIds("albums","artistid",id))

@app.route("/artist/albums/id/<string:id>")
def artist_albums_id(id):
    artistAlbumIds = getIds("albums","artistid",id)
    r = []
    for artistAlbumId in artistAlbumIds:
        r.append(album_id(artistAlbumId,True))
    return getResponse(r)

########################################################################################################################################################################
#-- Routen "/album/" --

@app.route("/album/ids")
def album_ids():
    return getResponse(getIds("albums"))

@app.route("/album/id/<string:id>")
def album_id(id,internal = False):
    
    #Um Daten zu sparen, die Tracks nicht direkt ausgeben
    albumDict = getAlbumById(id)
    if len(albumDict) > 0:
        albumDict["tracks"] = list()

    if internal: return albumDict
    return getResponse(albumDict)

@app.route("/album/tracks/id/<string:id>")
def album_tracks_id(id):
    return getResponse(getAlbumTracks(id))

########################################################################################################################################################################
#-- Routen "/author/" --

@app.route("/author/ids")
def author_ids():
    return getResponse(getIds("authors"))

@app.route("/author/id/<string:id>")
def author_id(id,internal = False):
    authorDict = getObjectFromDB("authors",id,Author)
    if internal: return authorDict
    return getResponse(authorDict)

@app.route("/author/all")
def author_all():
    authorIds = getIds("authors")
    r = []
    for authorId in authorIds:
        r.append(author_id(authorId,True))
    return getResponse(r)

@app.route("/author/audiobookids/<string:id>")
def author_audiobookids(id):
    return getResponse(getIds("audiobooks","authorid",id))

@app.route("/author/audiobooks/id/<string:id>")
def author_audiobooks_id(id):
    authorAudiobookIds = getIds("audiobooks","authorid",id)
    r = []
    for authorAudiobookId in authorAudiobookIds:
        r.append(audiobook_id(authorAudiobookId,True))
    return getResponse(r)

########################################################################################################################################################################
#-- Routen "/audiobook/" --

@app.route("/audiobook/ids")
def audiobook_ids():
    return getResponse(getIds("audiobooks"))

@app.route("/audiobook/id/<string:id>")
def audiobook_id(id,internal = False):
    
    #Um Daten zu sparen, die Tracks nicht direkt ausgeben
    audioBookDict = getAudioBookById(id)
    if len(audioBookDict) > 0:
        audioBookDict["tracks"] = list()

    if internal: return audioBookDict
    return getResponse(audioBookDict)

@app.route("/audiobook/tracks/id/<string:id>")
def audiobook_tracks_id(id):
    return getResponse(getAudioBookTracks(id)) 

########################################################################################################################################################################
#-- Routen "/channel/" --

@app.route("/channel/ids")
def channel_ids():
    return getResponse(getIds("channels"))

@app.route("/channel/id/<string:id>")
def channel_id(id,internal = False):
    channelDict = getChannelById(id)
    if internal: return channelDict
    return getResponse(channelDict)

@app.route("/channel/all")
def channel_all():
    channelIds = getIds("channels")
    r = []
    for channelId in channelIds:
        r.append(channel_id(channelId,True))
    return getResponse(r)

@app.route("/channel/previous/id/<string:id>")
def channel_previous_id(id):
    return getResponse(getPreviousChannel(id))

@app.route("/channel/next/id/<string:id>")
def channel_next_id(id):
    return getResponse(getNextChannel(id))

########################################################################################################################################################################
#-- Routen "/curatedplaylist/" --

@app.route("/curatedplaylist/ids")
def curatedplaylist_ids():
    return getResponse(getIds("curatedplaylists"))

@app.route("/curatedplaylist/id/<string:id>")
def curatedplaylist_id(id,internal = False):
    
    #Um Daten zu sparen, die Tracks nicht direkt ausgeben
    curatedPlaylistDict = getObjectFromDB("curatedplaylists",id,CuratedPlaylist)
    if len(curatedPlaylistDict) > 0:
        curatedPlaylistDict["tracks"] = list()

    if internal: return curatedPlaylistDict
    return getResponse(curatedPlaylistDict)

@app.route("/curatedplaylist/all")
def curatedplaylist_all():
    curatedplaylistIds = getIds("curatedplaylists")
    r = []
    for curatedplaylistId in curatedplaylistIds:
        r.append(curatedplaylist_id(curatedplaylistId,True))
    return getResponse(r)

@app.route("/curatedplaylist/tracks/id/<string:id>")
def curatedplaylist_tracks_id(id):
    return getResponse(getCuratedPlaylistTracks(id))

########################################################################################################################################################################
#-- Routen "/podcast/" --

@app.route("/podcast/ids")
def podcast_ids():
    return getResponse(getIds("podcasts"))

@app.route("/podcast/id/<string:id>")
def podcast_id(id,internal = False):
    podcastDict = getObjectFromDB("podcasts",id,Podcast)
    if internal: return podcastDict
    return getResponse(podcastDict)

@app.route("/podcast/all")
def podcast_all():
    podcastIds = getIds("podcasts")
    r = []
    for podcastId in podcastIds:
        r.append(podcast_id(podcastId,True))
    return getResponse(r)

@app.route("/podcast/episodes/id/<string:id>")
def podcast_episodes(id):
    return getResponse(getPodcastEpisodes(id))