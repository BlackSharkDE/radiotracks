########################################################################################################################################################################
#
# Indexer für Autoren und deren Audio-Books
#
########################################################################################################################################################################

import json
import mariadb

import jfiles

from _basic import Author, AudioBook, AudioTrack, RadiotracksLog, RadiotracksDBConnection

########################################################################################################################################################################

class IndexAuthors:

    #-- Konstruktor --
    #@param Indexer Ein Indexer-Objekt
    def __init__(self,indexer):
        self.indexer       = indexer
        self.rdbc          = RadiotracksDBConnection()
        self.pathOfAuthors = self.indexer.mediaFolderPath + "/author" #Gesamter Pfad in den "media/author/"-Ordner

    #Indexiert die Autoren und deren Audio-Books. (void - Funktion)
    def index(self):
        RadiotracksLog.log("IndexAuthors","Indexing Authors and their Audio-Books")

        #Alle Author-Ordner in "media/author/"
        for authorFolder in jfiles.getAllDirectoriesInPath(self.pathOfAuthors):

            path = self.pathOfAuthors + "/" + authorFolder

            #Author
            author           = Author()
            author.id        = self.indexer.generateId(path)
            author.name      = authorFolder
            author.path      = path
            author.mediaPath = self.indexer.getMediaPath(author.path)
            author.cover     = author.mediaPath + "/" + self.indexer.findCover(author.path)

            #Alle AudioBook-Ordnernamen
            authorAudioBookFolders = jfiles.getAllDirectoriesInPath(author.path)

            #Anzahl der AudioBooks bestimmen
            author.audioCollectionCount = len(authorAudioBookFolders)

            #Author in Datenbank speichern
            authorValuesList = list(author.toDict().values())
            authorValuesList.pop(5) #"audioCollections"-Value entfernen
            authorValuesList.extend(authorValuesList) #Liste mit sich selbst extenden, damit die Werte in der Datenbank entsprechend geupdatet werden
            try:
                self.rdbc.databaseCursor.execute(RadiotracksDBConnection.getInsertSQL("authors"),authorValuesList)
            except mariadb.Error as e:
                print(f"(IndexAuthors/Author) DB-error: {e}")

            #AudioBook-Objekte erstellen und in Datenbank speichern
            for audioBookFolder in authorAudioBookFolders:

                path = author.path + "/" + audioBookFolder

                #AudioBook
                audiobook           = AudioBook()
                audiobook.id        = self.indexer.generateId(path)
                audiobook.name      = self.indexer.generateName(audioBookFolder)
                audiobook.path      = path
                audiobook.mediaPath = self.indexer.getMediaPath(audiobook.path)
                audiobook.cover     = audiobook.mediaPath + "/" + self.indexer.findCover(audiobook.path)
                audiobook.published = self.indexer.generatePublished(audioBookFolder)

                #Tracks des AudioBook
                for audioFileInFolder in jfiles.getAllFilesInPath(audiobook.path,"mp3",False,False,True):

                    #AudioTrack erstellen
                    audiotrack           = AudioTrack()
                    audiotrack.path      = audiobook.path + "/" + audioFileInFolder
                    audiotrack.mediaPath = audiobook.mediaPath + "/" + audioFileInFolder
                    audiotrack.filename  = audioFileInFolder
                    audiotrack.duration  = self.indexer.getDuration(audiotrack.path)
                    audiotrack.title     = self.indexer.generateTitle(audiotrack.path)

                    #AudioTrack dem AudioBook hinzufügen
                    audiobook.tracks.append(audiotrack)
                    audiobook.trackCount += 1
                    audiobook.duration += audiotrack.duration

                #Klappentext einlesen
                audiobook.blurb = (self.indexer.getDescriptionJson(audiobook.path)).get("blurb","")

                #AudioBook in Datenbank speichern
                audioBookValuesList = list(audiobook.toDict().values())
                audioBookValuesList.insert(0,author.id) #Hinzufügen der Author-ID
                audioBookValuesList[7] = json.dumps(audioBookValuesList[7]) #Die Dictionaries als JSON-String exportieren
                audioBookValuesList.extend(audioBookValuesList) #Liste mit sich selbst extenden, damit die Werte in der Datenbank entsprechend geupdatet werden
                try:
                    self.rdbc.databaseCursor.execute(RadiotracksDBConnection.getInsertSQL("audiobooks"),audioBookValuesList)
                except mariadb.Error as e:
                    print(f"(IndexAuthors/AudioBook) DB-error: {e}")

            self.rdbc.databaseConnection.commit()

        self.rdbc.closeDatabaseConnection()
        RadiotracksLog.log("IndexAuthors","Done")