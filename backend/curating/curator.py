########################################################################################################################################################################
#
# Management zum Kuratieren der automatisierten "CuratedPlaylist"
#
########################################################################################################################################################################

import threading
import time
import json

from _basic import RadiotracksDBConnection, RadiotracksLog, CuratedPlaylist, runMultithreadedTask

from .selectors import dailyArtist, dailyRandom, oneYear, shorts

########################################################################################################################################################################

class Curator(threading.Thread):

    #Dictionary, welches die IDs von Curated-Playlists (siehe Datenbank) zu den Selektor-Funtionen mappt
    # "CuratedPlaylist-ID": Functionpointer
    selectorMapping = {
        #"4b2b807d60c9d48cfecef8b027ebf165": dailyArtist,
        #"db0151076a73d145548dc951284d5e78": dailyRandom,
        #"27c170ac94a7820088a5b87bc3bf820b": oneYear,
        #"58022a6809d1fdb839b3875f9ba6a074": shorts
    }
    
    #-- Konstruktor --
    def __init__(self):
        threading.Thread.__init__(self) #Parent-Konstruktor (Thread)

        #Für Endlosschleife in "run"-Methode
        self.keeprunning = True

    #Kuratiert ein CuratedPlaylist-Objekt. (void - Funktion)
    #@param String ID Des CuratedPlaylist-Objekts
    def curatePlaylist(curatedPlaylistId):

        #Datenbankverbindung
        rdbc = RadiotracksDBConnection()

        #CuratedPlaylist aus der Datenbank anhand der ID laden
        rdbc.databaseCursor.execute("SELECT * FROM `curatedplaylists` WHERE `id` = ?",[curatedPlaylistId])
        theCuratedPlaylist = rdbc.databaseCursor.fetchall()
        
        #Wenn die Playlist erfolgreich gefunden wurde
        if len(theCuratedPlaylist) == 1:
            theCuratedPlaylist = CuratedPlaylist.fromDBTuple(theCuratedPlaylist[0])

            #Prüfe, ob Update benötigt wird
            #-> Wenn letztes Update noch nie gemacht wurde
            #ODER
            #-> Wenn das letzte Update + Intervall in der Vergangenheit liegt (also passiert sein müsste)
            if theCuratedPlaylist.lastUpdate == 0 or (theCuratedPlaylist.lastUpdate + theCuratedPlaylist.updateInterval) < int(time.time()):
                #Curator-Funktion mit dem geladenen Objekt starten
                newCuratedPlaylist = (Curator.selectorMapping[theCuratedPlaylist.id])(theCuratedPlaylist)

                #Liste mit neuen Track-Dicts
                newCuratedPlaylistTrackList = []

                #Liste mit Tracks durchgehen und ggf. konvertieren
                for track in newCuratedPlaylist.tracks:
                    if type(track) != dict:
                        #Ist der Track kein Dict => Umwandeln und anhängen
                        newCuratedPlaylistTrackList.append(track.toDict())
                    else:
                        #Der Track ist ein Dict => Nur anhängen
                        newCuratedPlaylistTrackList.append(track)

                #Datenbank updaten
                rdbc.databaseCursor.execute(
                    "UPDATE `curatedplaylists` SET `published` = ?, `tracks` = ?, `trackCount` = ?, `duration` = ?, `description` = ?, `updateInterval` = ?, `lastUpdate` = ? WHERE `id` = ?",
                    [
                        newCuratedPlaylist.published,
                        json.dumps(newCuratedPlaylistTrackList),
                        newCuratedPlaylist.trackCount,
                        newCuratedPlaylist.duration,
                        newCuratedPlaylist.description,
                        newCuratedPlaylist.updateInterval,
                        int(time.time()), #Update-Zeitpunkt (jetzt) festlegen
                        curatedPlaylistId
                    ]
                )
                rdbc.databaseConnection.commit()
                RadiotracksLog.log("Curator","Updated CuratedPlaylist '" + theCuratedPlaylist.name + "'")

        rdbc.closeDatabaseConnection()

    #Thread-Methode (void - Funktion)
    def run(self):

        #Anzahl der gemappten CuratedPlaylist
        curatedPlaylistCount = len(Curator.selectorMapping)
        RadiotracksLog.log("Curator","Found " + str(curatedPlaylistCount) + " mapped CuratedPlaylist for curation")

        #Nur ausführen, wenn es Mappings gibt
        if curatedPlaylistCount > 0:

            #Laden der CuratedPlaylist-IDs aus dem selectorMapping-Dict
            curatedPlaylistIds = list(Curator.selectorMapping.keys())

            #So lange bis nicht mehr ausgeführt werden soll
            while self.keeprunning:

                #CuratedPlaylist-Kuratierungen erstellen
                runMultithreadedTask(Curator.curatePlaylist,curatedPlaylistIds)

                #Verhindere, dass der Thread zu viele Cycles und Datenbankverbindungen macht
                time.sleep(2)
        
        RadiotracksLog.log("Curator","Thread exited")

    #Beendet den Thread. (void - Funktion)
    def stopCurating(self):
        self.keeprunning = False
        RadiotracksLog.log("Curator","Stopped Curating (please wait for pending curation-Threads to finish)")