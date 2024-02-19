########################################################################################################################################################################
#
# Indexer für kuratierte Playlists
#
########################################################################################################################################################################

import json
import mariadb

import jfiles

from _basic import CuratedPlaylist, RadiotracksLog, RadiotracksDBConnection

########################################################################################################################################################################

class IndexCuratedPlaylists:

    #-- Konstruktor --
    #@param Indexer Ein Indexer-Objekt
    def __init__(self,indexer):
        self.indexer         = indexer
        self.rdbc            = RadiotracksDBConnection()
        self.pathOfPlaylists = self.indexer.mediaFolderPath + "/curatedplaylist" #Gesamter Pfad in den "media/curatedplaylist/"-Ordner

    #Indexiert die kuratierten Playlists. (void - Funktion)
    def index(self):
        RadiotracksLog.log("IndexCuratedPlaylists","Indexing curated Playlists (without parameters / empty, because curating will change them)")

        #Alle Playlist-Ordner in "media/curatedplaylist/"
        for curatedPlaylistFolder in jfiles.getAllDirectoriesInPath(self.pathOfPlaylists):

            path = self.pathOfPlaylists + "/" + curatedPlaylistFolder

            #CuratedPlaylist
            curatedplaylist             = CuratedPlaylist()
            curatedplaylist.id          = self.indexer.generateId(path)
            curatedplaylist.name        = curatedPlaylistFolder
            curatedplaylist.path        = path
            curatedplaylist.mediaPath   = self.indexer.getMediaPath(curatedplaylist.path)
            curatedplaylist.cover       = curatedplaylist.mediaPath + "/" + self.indexer.findCover(curatedplaylist.path)

            #CuratedPlaylist in Datenbank speichern
            curatedplaylistValuesList = list(curatedplaylist.toDict().values())
            curatedplaylistValuesList[6] = json.dumps(curatedplaylistValuesList[6]) #Leere Liste als JSON
            curatedplaylistValuesList.extend(curatedplaylistValuesList) #Liste mit sich selbst extenden, damit die Werte in der Datenbank entsprechend geupdatet werden
            try:
                #Statement erstellen lassen
                statement = RadiotracksDBConnection.getInsertSQL("curatedplaylists")

                #Alle Spalten nach `published` (inklusive) sollen nicht überschrieben werden
                statement = statement[0:statement.index(", `published`")]

                #Werte aus der Werte-Liste entfernen
                curatedplaylistValuesList.pop(23) #`lastUpdate`
                curatedplaylistValuesList.pop(22) #`updateInterval`
                curatedplaylistValuesList.pop(21) #`description`
                curatedplaylistValuesList.pop(20) #`duration`
                curatedplaylistValuesList.pop(19) #`trackCount`
                curatedplaylistValuesList.pop(18) #`tracks`
                curatedplaylistValuesList.pop(17) #`published`

                self.rdbc.databaseCursor.execute(statement,curatedplaylistValuesList)
            except mariadb.Error as e:
                print(f"(IndexCuratedPlaylists) DB-error: {e}")
        
            self.rdbc.databaseConnection.commit()

        self.rdbc.closeDatabaseConnection()
        RadiotracksLog.log("IndexCuratedPlaylists","Done")