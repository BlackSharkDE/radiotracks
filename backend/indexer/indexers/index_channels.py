########################################################################################################################################################################
#
# Indexer für Channel
#
########################################################################################################################################################################

import json
import mariadb

import jfiles

from _basic import LightChannel, InternetChannel, AdvancedChannel, AudioFile, RadiotracksLog, RadiotracksDBConnection

########################################################################################################################################################################

class IndexChannels:

    #-- Konstruktor --
    #@param Indexer Ein Indexer-Objekt
    def __init__(self,indexer):
        self.indexer       = indexer
        self.rdbc          = RadiotracksDBConnection()
        self.pathOfChannel = self.indexer.mediaFolderPath + "/channel" #Gesamter Pfad in den "media/channel/"-Ordner

    #Erstellt eine List mit AudioFile-Objekten anhand eines angegeben Pfades
    #@param String Pfad, in dem die Audio-Dateien liegen
    #@return List  Eine List mit AudioFiles / leere Liste, wenn Ordner nicht existiert
    def indexFolderOfAudioFiles(self,folderPath):

        #Alle Audio-Dateien in dem Ordner 
        folderTracks = list()

        if jfiles.pathExists(folderPath):

            for folderTrack in jfiles.getAllFilesInPath(folderPath,"mp3",False,False,True):

                #AudioFile
                audioFile           = AudioFile()
                audioFile.path      = folderPath + "/" + folderTrack
                audioFile.mediaPath = self.indexer.getMediaPath(audioFile.path)
                audioFile.filename  = folderTrack
                audioFile.duration  = self.indexer.getDuration(audioFile.path)

                #Leere Dateien können z.B. AdvancedMixer-Objekte stören
                if audioFile.duration > 0:
                    #AudioFile der Track-Liste hinzufügen
                    folderTracks.append(audioFile)

        return folderTracks

    #Indexiert die "InterceptionSources" für die "AdvancedChannel" (void - Funktion)
    #@param String Typ, kann "adverts", "news", "weather" sein
    def indexInterceptionSources(self,type):

        RadiotracksLog.log("IndexChannels/InterceptionSources","Indexing InterceptionSources (type = '" + type + "')")

        #Enspricht Unterorder "/adverts", "/news", "/weather" in "/channel"
        typeFolderPath = self.pathOfChannel + "/" + type

        #Alle Ordner des jeweiligen "type" durchgehen
        for folder in jfiles.getAllDirectoriesInPath(typeFolderPath):

            #Alle Audio-Dateien in dem Unterordner des "type"
            audioFilesList = self.indexFolderOfAudioFiles(typeFolderPath + "/" + folder)
            audioFilesList = list(map(lambda x: x.toDict(),audioFilesList)) #Die AudioFile-Objekte in Dictionaries konvertieren

            #Unterordner des "type" in Datenbank speichern
            typeFolderValuesList = [folder,type,json.dumps(audioFilesList)]
            typeFolderValuesList.extend(typeFolderValuesList) #Liste mit sich selbst extenden, damit die Werte in der Datenbank entsprechend geupdatet werden
            try:
                self.rdbc.databaseCursor.execute(RadiotracksDBConnection.getInsertSQL("interceptionsources"),typeFolderValuesList)
            except mariadb.Error as e:
                print(f"(IndexChannels/InterceptionSources) DB-error: {e}")

            self.rdbc.databaseConnection.commit()

        RadiotracksLog.log("IndexChannels/InterceptionSources","Done (type = '" + type + "')")

    #Indexiert die Channel. (void - Funktion)
    def indexChannels(self):

        RadiotracksLog.log("IndexChannels/Channels","Indexing Channels")

        channelsPath = self.pathOfChannel + "/channels"

        #Alle Channel-Ordner in "/channels"
        for channelFolder in jfiles.getAllDirectoriesInPath(channelsPath):

            #Gesamter Pfad des Channels
            channelPath = channelsPath + "/" + channelFolder

            #Einlesen der "description.json"
            cD = self.indexer.getDescriptionJson(channelPath)

            #Channel-Variable für einheitlichen INSERT
            channel = None

            #Anhand des Channel-Typ ensprechend verfahren
            channelType = cD.get("type", None)
            if channelType == "LightChannel":

                #LightChannel
                channel           = LightChannel()
                channel.id        = self.indexer.generateId(channelPath)
                channel.name      = channelFolder
                channel.path      = channelPath
                channel.mediaPath = self.indexer.getMediaPath(channel.path)
                channel.cover     = channel.mediaPath + "/" + self.indexer.findCover(channel.path)
                channel.hostedBy  = cD.get("hostedBy","Unknown")
                channel.tags      = cD.get("tags",list())

                #Tracks laden
                channel.tracks = self.indexFolderOfAudioFiles(channel.path)

                #Channel in Dict speichern
                channel = channel.toDict()
            elif channelType == "InternetChannel":

                #InternetChannel
                channel           = InternetChannel()
                channel.id        = self.indexer.generateId(channelPath)
                channel.name      = channelFolder
                channel.path      = channelPath
                channel.mediaPath = self.indexer.getMediaPath(channel.path)
                channel.cover     = channel.mediaPath + "/" + self.indexer.findCover(channel.path)
                channel.hostedBy  = cD.get("hostedBy","Unknown")
                channel.tags      = cD.get("tags",list())
                channel.streamUrl = cD.get("streamUrl","")

                #Channel in Dict speichern
                channel = channel.toDict()
            elif channelType == "AdvancedChannel":

                #AdvancedChannel
                channel                 = AdvancedChannel()
                channel.id              = self.indexer.generateId(channelPath)
                channel.name            = channelFolder
                channel.path            = channelPath
                channel.mediaPath       = self.indexer.getMediaPath(channel.path)
                channel.cover           = channel.mediaPath + "/" + self.indexer.findCover(channel.path)
                channel.hostedBy        = cD.get("hostedBy","Unknown")
                channel.tags            = cD.get("tags",list())
                channel.advertsFolder   = cD.get("advertsFolder","")
                channel.newsFolder      = cD.get("newsFolder","")
                channel.weatherFolder   = cD.get("weatherFolder","")
                channel.idTracks        = self.indexFolderOfAudioFiles(channel.path + "/id")
                channel.introTracks     = self.indexFolderOfAudioFiles(channel.path + "/intro")
                channel.monologueTracks = self.indexFolderOfAudioFiles(channel.path + "/monologue")

                allTimeTracks = self.indexFolderOfAudioFiles(channel.path + "/time")
                channel.timeTracks["morning"]   = [x for x in allTimeTracks if x.filename.lower().find('morning') > -1]
                channel.timeTracks["afternoon"] = [x for x in allTimeTracks if x.filename.lower().find('afternoon') > -1]
                channel.timeTracks["evening"]   = [x for x in allTimeTracks if x.filename.lower().find('evening') > -1]
                channel.timeTracks["night"]     = [x for x in allTimeTracks if x.filename.lower().find('night') > -1]

                allToTracks = self.indexFolderOfAudioFiles(channel.path + "/to")
                channel.toTracks["adverts"] = [x for x in allToTracks if x.filename.lower().find('to_ad') > -1]
                channel.toTracks["news"]    = [x for x in allToTracks if x.filename.lower().find('to_news') > -1]
                channel.toTracks["weather"] = [x for x in allToTracks if x.filename.lower().find('to_weather') > -1]

                channel.tracks = self.indexFolderOfAudioFiles(channel.path + "/tracks")

                #Channel in Dict speichern
                channel = channel.toDict()
            else:
                RadiotracksLog.log("IndexChannels/Channels","Can't index Channel '" + channelFolder + "', unknown or no 'type' given in 'description.json'")
            
            if type(channel) == dict:

                #Werte-Dictionary (universal für alle Channel) für den INSERT
                channelDict = {
                    "id"             : channel["id"],
                    "name"           : channel["name"],
                    "path"           : channel["path"],
                    "mediaPath"      : channel["mediaPath"],
                    "cover"          : channel["cover"],
                    "hostedBy"       : channel["hostedBy"],
                    "type"           : channelType,
                    "streamUrl"      : channel.get("streamUrl",""),
                    "advertsFolder"  : channel.get("advertsFolder",""),
                    "newsFolder"     : channel.get("newsFolder",""),
                    "weatherFolder"  : channel.get("weatherFolder",""),
                    "idTracks"       : json.dumps(channel["idTracks"]) if "idTracks" in channel else "{}",
                    "introTracks"    : json.dumps(channel["introTracks"]) if "introTracks" in channel else "{}",
                    "monologueTracks": json.dumps(channel["monologueTracks"]) if "monologueTracks" in channel else "{}",
                    "timeTracks"     : json.dumps(channel["timeTracks"]) if "timeTracks" in channel else "{}",
                    "toTracks"       : json.dumps(channel["toTracks"]) if "toTracks" in channel else "{}",
                    "tracks"         : json.dumps(channel["tracks"]) if "tracks" in channel else "{}"
                }

                #Channel in Datenbank speichern
                channelValuesList = list(channelDict.values())
                channelValuesList.extend(channelValuesList) #Liste mit sich selbst extenden, damit die Werte in der Datenbank entsprechend geupdatet werden
                try:
                    self.rdbc.databaseCursor.execute(RadiotracksDBConnection.getInsertSQL("channels"),channelValuesList)
                except mariadb.Error as e:
                    print(f"(IndexChannels/Channels) DB-error: {e}")

                #Tags des Channel in der Datenbank speichern
                for channelTag in channel["tags"]:
                    channelTagsValuesList = [channel["id"],channelTag]
                    channelTagsValuesList.extend(channelTagsValuesList) #Liste mit sich selbst extenden, damit die Werte in der Datenbank entsprechend geupdatet werden
                    try:
                        channelTagsSql  = "INSERT INTO `channeltags` (`channelid`,`tag`)"
                        channelTagsSql += "SELECT ?, ? "
                        channelTagsSql += "FROM `channeltags` "
                        channelTagsSql += "WHERE `channelid` = ? AND `tag` = ? HAVING COUNT(`channelid`) = 0"
                        self.rdbc.databaseCursor.execute(channelTagsSql,channelTagsValuesList)
                    except mariadb.Error as e:
                        print(f"(IndexChannels/Channels) DB-error: {e}")

            self.rdbc.databaseConnection.commit()

        RadiotracksLog.log("IndexChannels/Channels","Done")

    #Bündelungsfunktion für den Indexing-Prozess der Channel. (void - Funktion)
    #@param Bool Ob die "InterceptionSources" ignoriert werden sollen (DEBUG)
    #@param Bool Ob die "Channel" ignoriert werden sollen (DEBUG)
    def index(self,skipInterceptionSources = False,skipChannels = False):
        
        #-- InterceptionSources --
        if not skipInterceptionSources:
            self.indexInterceptionSources("adverts")
            self.indexInterceptionSources("news")
            self.indexInterceptionSources("weather")

        #-- Die Channel --
        if not skipChannels:
            self.indexChannels()

        self.rdbc.closeDatabaseConnection()