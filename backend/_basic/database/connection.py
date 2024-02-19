########################################################################################################################################################################
#
# Die Datenbankverbindung
# 
########################################################################################################################################################################

import re
import mariadb

from ..settings import getSetting
from ..logging import RadiotracksLog

from .setup import RadiotracksDBSetup

########################################################################################################################################################################

class RadiotracksDBConnection:

    #-- Statische Felder / Einstellungen => gelten für alle RadiotracksDBConnection-Objekte --
    databaseUser = None
    databasePass = None
    databaseHost = None
    databasePort = None

    #Lädt die Einstellungen für die Datenbankverbindungen. (void - Funktion)
    def loadSettings():
        databaseSettings = getSetting("database")
        RadiotracksDBConnection.databaseUser = databaseSettings["user"]
        RadiotracksDBConnection.databasePass = databaseSettings["pass"]
        RadiotracksDBConnection.databaseHost = databaseSettings["host"]
        RadiotracksDBConnection.databasePort = databaseSettings["port"]
        RadiotracksLog.log("RadiotracksDBConnection","Settings loaded")

    #(DEBUG) Zeigt due Einstellungen für die Datenbankverbindungen an. (void - Funktion)
    def showSettings():
        print("databaseUser: " + str(RadiotracksDBConnection.databaseUser))
        print("databasePass: " + str(RadiotracksDBConnection.databasePass))
        print("databaseHost: " + str(RadiotracksDBConnection.databaseHost))
        print("databasePort: " + str(RadiotracksDBConnection.databasePort))
    
    #-- Konstruktor --
    #@param bool Ob das Öffnen/Schließen der der Datenbankverbinding geloggt werden soll (OPTIONAL)
    def __init__(self,logOpeningClosingConnection = False):
        self.databaseCursor              = None
        self.databaseConnection          = None
        self.logOpeningClosingConnection = logOpeningClosingConnection
        self.setupDatabaseConnection()

    #Setzt die Attribute "databaseConnection" und "databaseCursor". (void - Funktion)
    #@param String Datenbankname (OPTIONAL)
    def setupDatabaseConnection(self,databaseName = "radiotracks"):
        if self.logOpeningClosingConnection:
            RadiotracksLog.log("RadiotracksDBConnection","Connecting to database host '" + RadiotracksDBConnection.databaseHost + "' with database '" + databaseName + "'")

        try:
            self.databaseConnection = mariadb.connect(
                user     = RadiotracksDBConnection.databaseUser,
                password = RadiotracksDBConnection.databasePass,
                host     = RadiotracksDBConnection.databaseHost,
                port     = RadiotracksDBConnection.databasePort,
                database = databaseName
            )
            self.databaseCursor = self.databaseConnection.cursor() #Cursor für Datenbankinteraktion
        except mariadb.ProgrammingError as e:
            RadiotracksLog.log("RadiotracksDBConnection","Encountered MariaDB ProgrammingError!")
            self.closeDatabaseConnection()
            RadiotracksDBSetup.testDatabaseSetup(self)
        except mariadb.Error as e:
            print(f"(RadiotracksDBConnection) DB-error: {e}")

    #Verbindung zur Datenbank beenden (void - Funktion)
    def closeDatabaseConnection(self):
        if self.logOpeningClosingConnection:
            RadiotracksLog.log("RadiotracksDBConnection","Closing connection to database host")

        if self.databaseCursor is not None:
            self.databaseCursor.close()
        if self.databaseConnection is not None:
            self.databaseConnection.close()

    #SQL-Insert-String für eine Tabelle erstellen
    #@param String  Name der Tabelle in der Datenbank (z.B. "authors")
    #@return String Der Insert-String
    def getInsertSQL(tableName):

        #Definition der Tabelle abfragen
        tableDefinition = RadiotracksDBSetup.databaseTableDefinitions[tableName]

        #Rückgabe-String
        insertSql = "INSERT INTO `" + tableName + "` VALUES ("

        #Spaltennamen aus SQL-Definition der Klasse herausfiltern
        columNames = tableDefinition.split(",")
        columNames = list(map(lambda x: x.strip(),columNames)) #Leerzeichen am Anfang und Ende von den Splatennamen entfernen
        columNames = [x for x in columNames if len(x) > 0 and x[0] == "`"] #Spaltennamen fangen immer mit "`" an
        columNames = list(map(lambda x: re.findall(r"`[\w]+`",x)[0],columNames)) #Entfernen der Datentypen / Spaltendefinition

        #Anzahl der Spalten
        columnAmount = len(columNames)

        #Platzhalter-Fragezeichen setzen
        for i in range(columnAmount):
            insertSql += "?"
            if i != (columnAmount - 1):
                insertSql += ","
        insertSql += ") ON DUPLICATE KEY UPDATE "
        
        #Spalten in String einfügen
        for i in range(columnAmount):
            column = columNames[i]
            insertSql += column + " = ?"
            if i != (columnAmount - 1):
                insertSql += ", "

        return insertSql