########################################################################################################################################################################
#
# Indexer für Podcasts und deren Episoden
#
########################################################################################################################################################################

import mariadb

import jfiles

from _basic import Podcast, PodcastEpisode, RadiotracksLog, RadiotracksDBConnection

########################################################################################################################################################################

class IndexPodcasts:

    #-- Konstruktor --
    #@param Indexer Ein Indexer-Objekt
    def __init__(self,indexer):
        self.indexer        = indexer
        self.rdbc           = RadiotracksDBConnection()
        self.pathOfPodcasts = self.indexer.mediaFolderPath + "/podcast" #Gesamter Pfad in den "media/podcast/"-Ordner

    #Indexiert die Podcasts und deren Episoden. (void - Funktion)
    def index(self):
        RadiotracksLog.log("IndexPodcasts","Indexing Podcasts and their Episodes")

        #Alle Podcast-Ordner "media/podcast/"
        for podcastFolder in jfiles.getAllDirectoriesInPath(self.pathOfPodcasts):

            path = self.pathOfPodcasts + "/" + podcastFolder

            #Podcast
            podcast              = Podcast()
            podcast.id           = self.indexer.generateId(path)
            podcast.name         = podcastFolder
            podcast.path         = path
            podcast.mediaPath    = self.indexer.getMediaPath(podcast.path)
            podcast.cover        = podcast.mediaPath + "/" + self.indexer.findCover(podcast.path)

            #"description" und "publisher" einlesen
            podcastDescription   = self.indexer.getDescriptionJson(podcast.path)
            podcast.description  = podcastDescription.get("description","")
            podcast.publisher    = podcastDescription.get("publisher","")

            #Episodenanzahl festlegen
            podcast.episodeCount = len(jfiles.getAllFilesInPath(podcast.path,"mp3"))

            #Podcast in Datenbank speichern
            podcastValuesList = list(podcast.toDict().values())
            podcastValuesList.pop(7) #"episodes"-Value entfernen
            podcastValuesList.extend(podcastValuesList) #Liste mit sich selbst extenden, damit die Werte in der Datenbank entsprechend geupdatet werden
            try:
                self.rdbc.databaseCursor.execute(RadiotracksDBConnection.getInsertSQL("podcasts"),podcastValuesList)
            except mariadb.Error as e:
                print(f"(IndexPodcasts/Podcast) DB-error: {e}")
            
            #Episoden des Podcasts
            for podcastEpisodeInFolder in jfiles.getAllFilesInPath(podcast.path,"mp3",False,False,True):

                #Podcast-Episode erstellen
                podcastEpisode             = PodcastEpisode()
                podcastEpisode.path        = podcast.path + "/" + podcastEpisodeInFolder
                podcastEpisode.mediaPath   = self.indexer.getMediaPath(podcastEpisode.path)
                podcastEpisode.filename    = podcastEpisodeInFolder
                podcastEpisode.duration    = self.indexer.getDuration(podcastEpisode.path)

                #"title" und "description" einlesen
                podcastEpisodeDescription  = self.indexer.getDescriptionJson(podcast.path,jfiles.getFilenameNoExtension(podcastEpisode.filename))
                podcastEpisode.title       = podcastEpisodeDescription.get("title","")
                podcastEpisode.description = podcastEpisodeDescription.get("description","")

                #Podcast-Episode in Datenbank speichern
                podcastEpisodeValuesList = list(podcastEpisode.toDict().values())
                podcastEpisodeValuesList.insert(0,podcast.id) #Hinzufügen der Podcast-ID
                podcastEpisodeValuesList.extend(podcastEpisodeValuesList) #Liste mit sich selbst extenden, damit die Werte in der Datenbank entsprechend geupdatet werden
                try:
                    self.rdbc.databaseCursor.execute(RadiotracksDBConnection.getInsertSQL("podcastepisodes"),podcastEpisodeValuesList)
                except mariadb.Error as e:
                    print(f"(IndexPodcasts/PodcastEpisode) DB-error: {e}")

            self.rdbc.databaseConnection.commit()

        self.rdbc.closeDatabaseConnection()
        RadiotracksLog.log("IndexPodcasts","Done")