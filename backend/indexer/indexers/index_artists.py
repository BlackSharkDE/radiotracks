########################################################################################################################################################################
#
# Indexer für Artists und deren Alben samt Tracks
#
########################################################################################################################################################################

import mariadb

import jfiles

from _basic import Artist, Album, AudioTrack, RadiotracksLog, RadiotracksDBConnection

########################################################################################################################################################################

class IndexArtists:

    #-- Konstruktor --
    #@param Indexer Ein Indexer-Objekt
    def __init__(self,indexer):
        self.indexer       = indexer
        self.rdbc          = RadiotracksDBConnection()
        self.pathOfArtists = self.indexer.mediaFolderPath + "/artist" #Gesamter Pfad in den "media/artist/"-Ordner

    #Indexiert die Artists und deren Alben samt Tracks. (void - Funktion)
    def index(self):
        RadiotracksLog.log("IndexArtists","Indexing Artists, Albums and their Tracks")

        #Alle Artist-Ordner in "media/artist/"
        for artistFolder in jfiles.getAllDirectoriesInPath(self.pathOfArtists):

            path = self.pathOfArtists + "/" + artistFolder

            #Artist
            artist           = Artist()
            artist.id        = self.indexer.generateId(path)
            artist.name      = artistFolder
            artist.path      = path
            artist.mediaPath = self.indexer.getMediaPath(artist.path)
            artist.cover     = artist.mediaPath + "/" + self.indexer.findCover(artist.path)

            #Alle Album-Ordnernamen
            artistAlbumFolders = jfiles.getAllDirectoriesInPath(artist.path)

            #Anzahl der Alben bestimmen
            artist.audioCollectionCount = len(artistAlbumFolders)

            #Artist in Datenbank speichern
            artistValuesList = list(artist.toDict().values())
            artistValuesList.pop(5) #"audioCollections"-Value entfernen
            artistValuesList.extend(artistValuesList) #Liste mit sich selbst extenden, damit die Werte in der Datenbank entsprechend geupdatet werden
            try:
                self.rdbc.databaseCursor.execute(RadiotracksDBConnection.getInsertSQL("artists"),artistValuesList)
            except mariadb.Error as e:
                print(f"(IndexArtists/Artist) DB-error: {e}")
            
            #Alben des Artist
            for albumFolder in artistAlbumFolders:

                path = artist.path + "/" + albumFolder

                #Album
                album           = Album()
                album.id        = self.indexer.generateId(path)
                album.name      = self.indexer.generateName(albumFolder)
                album.path      = path
                album.mediaPath = self.indexer.getMediaPath(album.path)
                album.cover     = album.mediaPath + "/" + self.indexer.findCover(album.path)
                album.published = self.indexer.generatePublished(albumFolder)

                #Tracks des Albums
                for audioTrackInFolder in jfiles.getAllFilesInPath(album.path,"mp3",False,False,True):

                    #AudioTrack
                    audioTrack           = AudioTrack()
                    audioTrack.path      = album.path + "/" + audioTrackInFolder
                    audioTrack.mediaPath = self.indexer.getMediaPath(audioTrack.path)
                    audioTrack.filename  = audioTrackInFolder
                    audioTrack.duration  = self.indexer.getDuration(audioTrack.path)
                    audioTrack.title     = self.indexer.generateTitle(audioTrack.path)

                    #AudioTrack dem Album hinzufügen
                    album.tracks.append(audioTrack)
                    album.trackCount += 1
                    album.duration += audioTrack.duration

                #Album in Datenbank speichern
                albumValuesList = list(album.toDict().values())
                albumValuesList.insert(0,artist.id) #Hinzufügen der Artist-ID
                albumValuesList.pop(7) #"tracks"-Value entfernen
                albumValuesList.extend(albumValuesList) #Liste mit sich selbst extenden, damit die Werte in der Datenbank entsprechend geupdatet werden
                try:
                    self.rdbc.databaseCursor.execute(RadiotracksDBConnection.getInsertSQL("albums"),albumValuesList)
                except mariadb.Error as e:
                    print(f"(IndexArtists/Album) DB-error: {e}")

                #Tracks des Albums in Datenbank speichern
                for audioTrack in album.tracks:
                    audioTrackValuesList = list(audioTrack.toDict().values())
                    audioTrackValuesList.insert(0,album.id) #Hinzufügen der Album-ID
                    audioTrackValuesList.extend(audioTrackValuesList) #Liste mit sich selbst extenden, damit die Werte in der Datenbank entsprechend geupdatet werden
                    try:
                        self.rdbc.databaseCursor.execute(RadiotracksDBConnection.getInsertSQL("albumtracks"),audioTrackValuesList)
                    except mariadb.Error as e:
                        print(f"(IndexArtists/AudioTrack) DB-error: {e}")

            self.rdbc.databaseConnection.commit()

        self.rdbc.closeDatabaseConnection()
        RadiotracksLog.log("IndexArtists","Done")