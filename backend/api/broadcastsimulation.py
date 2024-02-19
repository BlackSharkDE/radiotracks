########################################################################################################################################################################
#
# Reimplementation meines JavaScript-Scripts "broadcastsimulation.js"
#
# Wurde schon einmal in Radiotracks v3 so ähnlich umgesetzt.
#
# Für genauere Dokumentation bzw. Erklärung zur Funktionsweise, siehe original-Repository.
#
########################################################################################################################################################################

import datetime
import math

########################################################################################################################################################################

#Simuliert den Senderbetrieb
#@param Int  Gesamtdauer der Playlist in Sekunden
#@return Int Fiktiver Startpunkt in der Playlist in Sekunden
def simulatePlaylist(playlistLength):

    #Sekunden, die seit dem fiktiven Startdatum vergangen sind.
    def getSecondsSinceStart():
        dtStart = datetime.datetime(1990,1,1,0,0,0)
        dtNow   = datetime.datetime.now()
        diff = dtNow - dtStart
        diff = diff.total_seconds()
        diff = math.ceil(diff)
        return diff

    secsSinceStart = getSecondsSinceStart()
    ran = secsSinceStart / playlistLength
    percent = ran % 1
    secs = (percent * playlistLength) / 100
    secs = math.ceil(secs * 100)
    return secs

#Sucht anhand der Startsekunden der Playlist den aktuellen Track heraus, der gerade spielen müsste
#@param Int    Startsekunden in der Playlist
#@param List   Liste mit AudioFile-Objekten
#@return Tuple Ein Tuple mit zwei Einträgen: [0] = Trackindex in der Playlist ; [1] = Startsekunden des Tracks selbst (Integer)
def searchStarttrackFromPlaylist(tracklistStartseconds,givenTracklist):

    tempTime = 0
    index = -1
    overhead = 0

    if tracklistStartseconds == 0:
        index = 0
        overhead = 0
    else:
        while tempTime < tracklistStartseconds:
            index += 1
            tempTime += givenTracklist[index].duration

        overhead = tempTime - tracklistStartseconds

        while overhead > givenTracklist[index].duration:
            index += 1
            if index > len(givenTracklist) - 1:
                index = 0
            overhead -= givenTracklist[index].duration

            if overhead == givenTracklist[index].duration:
                index += 1
                if index > len(givenTracklist) - 1:
                    index = 0

        overhead = abs(overhead - givenTracklist[index].duration)

    return (index,overhead)

#Führt die Simulation durch
#@param Siehe  "searchStarttrackFromPlaylist" => givenTracklist
#@param Siehe  "simulatePlaylist" => playlistLength
#@return Siehe "searchStarttrackFromPlaylist"
def broadcastsimulation(trackList,trackListDuration):
    startseconds = simulatePlaylist(trackListDuration)
    return searchStarttrackFromPlaylist(startseconds,trackList)