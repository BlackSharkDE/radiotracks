########################################################################################################################################################################
#
# Die Kuratierungsfunktionen für verschiedene CuratedPlaylist
#
########################################################################################################################################################################

import datetime
import time

from _basic import getRandomItemFromList
from api import getIds, getAlbumById

########################################################################################################################################################################
#-- Sonstige Funktionen --

#Berechnet Zeit bis zum nächsten, täglichen Zielzeitpunkt (dient zum einpendeln der täglichen Playlists).
#-> Wenn der Zeitpunkt in der Vergangenheit liegt, dann bis Zielzeitpunkt am nächsten Tag
#@param Int  Stunde
#@param Int  Minute
#@return Int Zeit in Sekunden
def balanceDaily(targetHour,targetMinute):
    
    #Startwerte festlegen
    today      = datetime.datetime.today()
    targetTime = today.replace(hour = targetHour, minute = targetMinute, second = 0, microsecond = 0)

    #Berechnet die Zeit in Sekunden zur Zielstunde und Zielminute
    #@return Int Zeit in Sekunden
    def target():
        nonlocal targetTime
        target = int(targetTime.timestamp()) #Unix-Zeitstempel
        return target - int(time.time())

    #Berechnen
    delta = target()

    #Sollte "delta" negativ sein (in der Vergangenheit liegen)
    if delta < 0:
        #Zeitpunkt für nächsten Tag
        targetTime = targetTime + datetime.timedelta(days=1)
        
        #Neu berechnen
        delta = target()
    
    return delta

#Setzt die Track-Attribute einer CuratedPlaylist zurück. (void - Funktion)
#@param  CuratedPlaylist Ein / das CuratedPlaylist-Objekt
#@return CuratedPlaylist Angepasstes / verändertes CuratedPlaylist-Objekt
def resetCuratedPlaylistTracks(aCuratedPlaylist):
    aCuratedPlaylist.tracks     = list()
    aCuratedPlaylist.trackCount = 0
    aCuratedPlaylist.duration   = 0
    return aCuratedPlaylist

########################################################################################################################################################################
#-- Selector-Funktionen --

#Kuratiert die "Daily Artist"-Playlist. (void - Funktion)
#@param  CuratedPlaylist Ein / das CuratedPlaylist-Objekt
#@return CuratedPlaylist Angepasstes / verändertes CuratedPlaylist-Objekt
def dailyArtist(curatedPlaylist):

    if curatedPlaylist.lastUpdate == 0:
        #-- Wurde noch nie geupdated / initialer Zustand --
        curatedPlaylist.published      = str(datetime.datetime.now().year)
        curatedPlaylist.description    = "Jeden Tag ein neuer Artist"
        curatedPlaylist.updateInterval = balanceDaily(1,5) #Die nächste Zielausführungszeit berechnen
    elif curatedPlaylist.updateInterval > 0 and curatedPlaylist.lastUpdate > 0:
        #-- Erstes Update wurde schon einmal ausgeführt --
        curatedPlaylist.updateInterval = 86000 #Ausführungsintervall auf täglich umstellen

    curatedPlaylist = resetCuratedPlaylistTracks(curatedPlaylist)

    #Zufällige Artist-ID heraussuchen
    artistIds = getIds("artists")
    todayArtistId = getRandomItemFromList(artistIds)
    
    #Alle Alben-IDs des Artist abrufen
    todayArtistAlbumIds = getIds("albums","artistid",todayArtistId)

    #Alle Album-Tracks in eine Playlist packen
    tracks = list()
    for id in todayArtistAlbumIds:
        album = getAlbumById(id)
        tracks.extend(album["tracks"])
        curatedPlaylist.duration += album["duration"]

    #Der CuratedPlaylist die Tracks und Track-Anzahl zuweisen
    curatedPlaylist.tracks     = tracks
    curatedPlaylist.trackCount = len(tracks)

    return curatedPlaylist

#Kuratiert die "Daily Random"-Playlist. (void - Funktion)
#@param  CuratedPlaylist Ein / das CuratedPlaylist-Objekt
#@return CuratedPlaylist Angepasstes / verändertes CuratedPlaylist-Objekt
def dailyRandom(curatedPlaylist):

    if curatedPlaylist.lastUpdate == 0:
        #-- Wurde noch nie geupdated / initialer Zustand --
        curatedPlaylist.published      = str(datetime.datetime.now().year)
        curatedPlaylist.description    = "Jeden Tag neue zufällige Tracks"
        curatedPlaylist.updateInterval = balanceDaily(1,10) #Die nächste Zielausführungszeit berechnen
    elif curatedPlaylist.updateInterval > 0 and curatedPlaylist.lastUpdate > 0:
        #-- Erstes Update wurde schon einmal ausgeführt --
        curatedPlaylist.updateInterval = 86000 #Ausführungsintervall auf täglich umstellen

    curatedPlaylist = resetCuratedPlaylistTracks(curatedPlaylist)

    #Alle Alben-IDs
    albumIds = getIds("albums")
    
    #Alle Tracks aus der Datenbank laden
    allTracks = list()
    for id in albumIds:
        allTracks.extend(getAlbumById(id)["tracks"])

    #20 zufällige Tracks heraussuchen
    for i in range(20):
        track = getRandomItemFromList(allTracks,True)
        if track is not None: #Sollten zu wenig Tracks vorhanden sein
            curatedPlaylist.tracks.append(track)
            curatedPlaylist.trackCount += 1
            curatedPlaylist.duration   += track["duration"]
    
    return curatedPlaylist

#Kuratiert die "One Year"-Playlist. (void - Funktion)
#@param  CuratedPlaylist Ein / das CuratedPlaylist-Objekt
#@return CuratedPlaylist Angepasstes / verändertes CuratedPlaylist-Objekt
def oneYear(curatedPlaylist):

    if curatedPlaylist.lastUpdate == 0:
        #-- Wurde noch nie geupdated / initialer Zustand --
        curatedPlaylist.published      = str(datetime.datetime.now().year)
        curatedPlaylist.description    = "Jeden Tag ein neuer Track"
        curatedPlaylist.updateInterval = balanceDaily(1,15) #Die nächste Zielausführungszeit berechnen
    elif curatedPlaylist.updateInterval > 0 and curatedPlaylist.lastUpdate > 0:
        #-- Erstes Update wurde schon einmal ausgeführt --
        curatedPlaylist.updateInterval = 86000 #Ausführungsintervall auf täglich umstellen

    #Am 01.01. jeden Jahres zurücksetzen
    today = datetime.datetime.today()
    if today.month == 1 and today.day == 1:
        curatedPlaylist = resetCuratedPlaylistTracks(curatedPlaylist)

    #Alle Alben-IDs
    albumIds = getIds("albums")

    #Zufällige Album-ID
    albumId = getRandomItemFromList(albumIds)

    #Das Album
    album = getAlbumById(albumId)

    #Zufälliger Track
    albumTrack = getRandomItemFromList(album["tracks"])

    #Der Playlist hinzufügen
    curatedPlaylist.tracks.append(albumTrack)
    curatedPlaylist.trackCount += 1
    curatedPlaylist.duration   += albumTrack["duration"]

    return curatedPlaylist

#Kuratiert die "Shorts"-Playlist. (void - Funktion)
#@param  CuratedPlaylist Ein / das CuratedPlaylist-Objekt
#@return CuratedPlaylist Angepasstes / verändertes CuratedPlaylist-Objekt
def shorts(curatedPlaylist):

    if curatedPlaylist.lastUpdate == 0:
        #-- Wurde noch nie geupdated / initialer Zustand --
        curatedPlaylist.published      = str(datetime.datetime.now().year)
        curatedPlaylist.description    = "Die kürzesten Tracks auf Radiotracks"
        curatedPlaylist.updateInterval = balanceDaily(1,20) #Die nächste Zielausführungszeit berechnen
    elif curatedPlaylist.updateInterval > 0 and curatedPlaylist.lastUpdate > 0:
        #-- Erstes Update wurde schon einmal ausgeführt --
        curatedPlaylist.updateInterval = 86000 #Ausführungsintervall auf täglich umstellen

    curatedPlaylist = resetCuratedPlaylistTracks(curatedPlaylist)

    #Alle Alben-IDs
    albumIds = getIds("albums")

    #Alle Tracks aus der Datenbank laden
    allTracks = list()
    for id in albumIds:
        allTracks.extend(getAlbumById(id)["tracks"])

    #Die kürzesten Tracks (kürzer als 90 Sekunden) heraussuchen
    for track in allTracks:
        if track["duration"] <= 90:
            curatedPlaylist.tracks.append(track)
            curatedPlaylist.trackCount += 1
            curatedPlaylist.duration   += track["duration"]

    return curatedPlaylist