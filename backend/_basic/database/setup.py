########################################################################################################################################################################
#
# Das Datenbanksetup
# 
########################################################################################################################################################################

from ..logging import RadiotracksLog

########################################################################################################################################################################

class RadiotracksDBSetup:

    #SQL-Definitionen der Basis-Klassen in "basic.py"
    basicClassesBasicSqlDefinitions = {
        "BasicType": "`id` CHAR(32) PRIMARY KEY, `name` VARCHAR(255), `path` VARCHAR(255), `mediaPath` VARCHAR(255), `cover` VARCHAR(255),",
        "AudioFile": "`path` VARCHAR(255) UNIQUE, `mediaPath` VARCHAR(255), `filename` VARCHAR(255), `duration` INT,",
    }
    basicClassesSqlDefinitions = {
        #-- Dieses Dictionary für Referenzen benutzen! --
        "BasicType"       : basicClassesBasicSqlDefinitions["BasicType"],
        "AudioFile"       : basicClassesBasicSqlDefinitions["AudioFile"],
        "AudioTrack"      : basicClassesBasicSqlDefinitions["AudioFile"] + " `title` VARCHAR(255),",
        "AudioCollection" : basicClassesBasicSqlDefinitions["BasicType"] + " `published` CHAR(4), `tracks` JSON, `trackCount` INT, `duration` INT,",
        "AudioCreator"    : basicClassesBasicSqlDefinitions["BasicType"] + " `audioCollectionCount` INT"
    }

    #Definitionen der Tabellen in der `radiotracks`-Datenbank
    databaseTableDefinitions = {

        #`artists`, `albums`, `albumtracks` - Tabellen
        "artists"    : basicClassesSqlDefinitions["AudioCreator"],
        "albums"     : "`artistid` CHAR(32), " + (basicClassesSqlDefinitions["AudioCollection"]).replace(" `tracks` JSON,","") + " FOREIGN KEY(`artistid`) REFERENCES `artists`(`id`)",
        "albumtracks": "`albumid` CHAR(32), " + basicClassesSqlDefinitions["AudioTrack"] + " FOREIGN KEY(`albumid`) REFERENCES `albums`(`id`)",
        
        #`authors`, `audiobooks` - Tabellen
        "authors"   : basicClassesSqlDefinitions["AudioCreator"],
        "audiobooks": "`authorid` CHAR(32), " + basicClassesSqlDefinitions["AudioCollection"] + " `blurb` TEXT, FOREIGN KEY(`authorid`) REFERENCES `authors`(`id`)",

        #`channel`, `interceptionsources` - Tabellen
        "channels": basicClassesSqlDefinitions["BasicType"] + \
        ' `hostedBy` VARCHAR(255), `type` ENUM("LightChannel","InternetChannel","AdvancedChannel"),' + \
        " `streamUrl` VARCHAR(512)," + \
        "`advertsFolder` VARCHAR(255), `newsFolder` VARCHAR(255), `weatherFolder` VARCHAR(255)," + \
        "`idTracks` JSON, `introTracks` JSON, `monologueTracks` JSON, `timeTracks` JSON, `toTracks` JSON, `tracks` JSON",
        #1. Zeile: Diese Attribute hat jeder Channel (LightChannel haben keine weiteren Attribute)
        #2. Zeile: InternetChannel (wenn kein InternetChannel, dieses Feld freilassen)
        #3. und 4. Zeile: AdvancedChannel (wenn kein AdvancedChannel, diese Felder freilassen)
        #==> Alle Channel haben die selbe Definition / Tabelle
        "interceptionsources": '`foldername` VARCHAR(255), `type` ENUM("adverts","news","weather"), `tracks` JSON UNIQUE',
        #^^ Hier werden die "advertsTracks", "newsTracks" und "weatherTracks" bzw. die referenzierten Ordnerinhalte gespeichert (verhindert Mehrfachspeicherung in `channel`-Tabelle)
        "channeltags": "`channelid` CHAR(32), `tag` VARCHAR(255), FOREIGN KEY(`channelid`) REFERENCES `channels`(`id`)",
        #^^ Tags der Channel
        "channelmixes": "`advancedChannelId` CHAR(32), `tracks` JSON, `creationTime` INT UNSIGNED, `duration` SMALLINT UNSIGNED, `validFrom` INT UNSIGNED, `validTo` INT UNSIGNED",
        #^^ Mixes für AdvancedChannel-Objekte

        #`curatedplaylist` - Tabelle
        "curatedplaylists": basicClassesSqlDefinitions["AudioCollection"] + " `description` TEXT, `updateInterval` INT, `lastUpdate` INT",

        #`podcasts`, `podcastepisodes` - Tabellen
        "podcasts"       : basicClassesSqlDefinitions["BasicType"] + " `description` TEXT, `publisher` VARCHAR(255), `episodeCount` INT",
        "podcastepisodes": "`podcastid` CHAR(32), " + basicClassesSqlDefinitions["AudioFile"] + " `title` VARCHAR(255), `description` TEXT, FOREIGN KEY(`podcastid`) REFERENCES `podcasts`(`id`)"
    }

    #Testet das Datenbanksetup. (void - Funktion)
    #@param RadiotracksDBConnection Ein RadiotracksDBConnection-Objekt, das für das Testen benutzt werden kann
    def testDatabaseSetup(radiotracksDBConnection):
        RadiotracksLog.log("RadiotracksDBSetup","Checking if database exists...")
        radiotracksDBConnection.setupDatabaseConnection(databaseName="")
        radiotracksDBConnection.databaseCursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'radiotracks'")
        if len(radiotracksDBConnection.databaseCursor.fetchall()) == 1:
            RadiotracksLog.log("RadiotracksDBSetup","Database exists (don't know what's wrong)!")
        else:
            RadiotracksLog.log("RadiotracksDBSetup","Database does not exist!")
            RadiotracksDBSetup.databaseSetup(radiotracksDBConnection)
    
    #Führt das Datenbanksetup aus. (void - Funktion)
    #@param RadiotracksDBConnection Ein RadiotracksDBConnection-Objekt, das für das Setup benutzt werden kann
    def databaseSetup(radiotracksDBConnection):
        RadiotracksLog.log("RadiotracksDBSetup","Running setup, please wait...")

        #Erstellen der Datenbank
        radiotracksDBConnection.databaseCursor.execute("CREATE SCHEMA `radiotracks` DEFAULT CHARACTER SET utf8")

        #Tabellen erstellen
        for tableName in RadiotracksDBSetup.databaseTableDefinitions.keys():
            tableDefintion = RadiotracksDBSetup.databaseTableDefinitions[tableName]
            radiotracksDBConnection.databaseCursor.execute("CREATE TABLE `radiotracks`.`" + tableName + "` (" + tableDefintion + ")")

        RadiotracksLog.log("RadiotracksDBSetup","Done setting up database. Reopening connection...")
        radiotracksDBConnection.closeDatabaseConnection()
        radiotracksDBConnection.setupDatabaseConnection()