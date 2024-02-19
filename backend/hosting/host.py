########################################################################################################################################################################
#
# AdvancedHost
#
# Updated und löscht alte AdvancedMix-Objekte der jeweiligen AdvancedChannel
#
########################################################################################################################################################################

import threading
import time
import json

from _basic import RadiotracksLog, RadiotracksDBConnection, AdvancedChannel, runMultithreadedTask
from .mixer import AdvancedMixer

########################################################################################################################################################################

class AdvancedHost(threading.Thread):

    #-- Konstruktor --
    def __init__(self):
        threading.Thread.__init__(self) #Parent-Konstruktor (Thread)

        #Datenbankverbindung (nur zum Laden der AdvancedChannel)
        self.rdbc = RadiotracksDBConnection()

        #Für Endlosschleife in "run"-Methode
        self.keeprunning = True

    #Übernimmt das Hosting für einen Channel. (void - Funktion)
    #@param AdvancedChannel Ein AdvancedChannel-Objekt
    def hostChannel(aAdvancedChannel):

        #Datenbankverbindung für diesen Channel
        rdbc = RadiotracksDBConnection()

        #Uhrzeit jetzt
        now = int(time.time())

        #Alte AdvancedMix-Objekte des AdvancedChannel löschen
        #(now - 30), damit die Mixes etwas später gelöscht werden
        rdbc.databaseCursor.execute("SELECT `advancedChannelId`, `creationTime`, `duration`, `validFrom`, `validTo` FROM `channelmixes` WHERE `advancedChannelId` = ? AND `validTo` < ?",[aAdvancedChannel.id,(now - 30)])
        oldMixes = rdbc.databaseCursor.fetchall()
        if len(oldMixes) > 0:
            for oldMix in oldMixes:
                rdbc.databaseCursor.execute("DELETE FROM `channelmixes` WHERE `advancedChannelId` = ? AND `creationTime` = ? AND `duration` = ? AND `validFrom` = ? AND `validTo` = ?",[aAdvancedChannel.id,oldMix[1],oldMix[2],oldMix[3],oldMix[4]])
            rdbc.databaseConnection.commit()

        #Prüfen, wie viele gültige AdvancedMix-Objekte für den AdvancedChannel gespeichert sind
        rdbc.databaseCursor.execute("SELECT * FROM `channelmixes` WHERE `advancedChannelId` = ? AND `validTo` >= ?",[aAdvancedChannel.id,now])
        validMixes = rdbc.databaseCursor.fetchall()
        
        #Wenn weniger als 2 valide AdvancedMix-Objekte gespeichert sind
        validMixCount = len(validMixes)
        if validMixCount < 2:

            #Liste mit neuen AdvancedMix-Objekten
            newAdvancedMixes = list()

            logDurations = ""

            #-- Entsprechende Anzahl an AdvancedMix-Objekten erstellen --
            if validMixCount == 0:
                #-- Gar keine AdvancedMix vorhanden --
                for i in range(2):

                    #Neuen erstellen
                    newMix = AdvancedMixer(aAdvancedChannel).createMix()
                    
                    #Die Validitätszeiten des zweiten AdvancedMix müssen angepasst werden
                    if i == 1:
                        newMix.adjustValidity(newAdvancedMixes[0].validTo + 1)
                    
                    #Der Liste mit neuen AdvancedMix-Objekten hinzufügen
                    newAdvancedMixes.append(newMix)
                
                logDurations = ", durations: " + str(newAdvancedMixes[0].duration) + " / " + str(newAdvancedMixes[1].duration)

            elif validMixCount == 1:
                #-- Ein valider AdvancedMix ist noch da --
                
                #Neuen erstellen
                newMix = AdvancedMixer(aAdvancedChannel).createMix()

                #Die Validitätszeiten des neuen AdvancedMix müssen angepasst werden
                newMix.adjustValidity(validMixes[0][5] + 1)
                
                #Der Liste mit neuen AdvancedMix-Objekten hinzufügen
                newAdvancedMixes.append(newMix)

                logDurations = ", duration: " + str(newMix.duration)

            #Neue AdvancedMix-Objekte in Datenbank speichern
            for newAdvancedMix in newAdvancedMixes:
                advancedMixValuesList = list(newAdvancedMix.toDict().values())
                advancedMixValuesList[1] = json.dumps(advancedMixValuesList[1]) #Die Dictionaries als JSON-String exportieren
                advancedMixValuesList.extend(advancedMixValuesList) #Liste mit sich selbst extenden, damit die Werte in der Datenbank entsprechend geupdatet werden
                rdbc.databaseCursor.execute(RadiotracksDBConnection.getInsertSQL("channelmixes"),advancedMixValuesList)
            
            rdbc.databaseConnection.commit()

            RadiotracksLog.log("AdvancedHost","Saved " + str(len(newAdvancedMixes)) + " new AdvancedMix for '" + aAdvancedChannel.id + "'" + logDurations)

        rdbc.closeDatabaseConnection()

    #Thread-Methode (void - Funktion)
    def run(self):

        #Einstellungen für AdvancedMixer-Objekte laden
        AdvancedMixer.loadSettings()

        #Alle AdvancedChannel-Objekte aus der Datenbank laden
        self.rdbc.databaseCursor.execute('SELECT * FROM radiotracks.channels WHERE `type` = "AdvancedChannel"')
        allAdvancedChannelTuples = self.rdbc.databaseCursor.fetchall()
        self.rdbc.closeDatabaseConnection()

        #Datenbankeinträge in Objekte umwandeln
        allAdvancedChannel = list()
        for advancedChannelTuple in allAdvancedChannelTuples:
            allAdvancedChannel.append(AdvancedChannel.fromDBTuple(advancedChannelTuple))

        #Anzahl der AdvancedChannel
        advancedChannelCount = len(allAdvancedChannel)
        RadiotracksLog.log("AdvancedHost","Loaded " + str(advancedChannelCount) + " AdvancedChannel to host")

        #Nur ausführen, wenn AdvancedChannel eingerichtet wurden
        if advancedChannelCount > 0:
        
            #So lange bis nicht mehr ausgeführt werden soll
            while self.keeprunning:

                #AdvancedChannel-Hosting erstellen
                runMultithreadedTask(AdvancedHost.hostChannel,allAdvancedChannel)

                #Verhindere, dass der Thread zu viele Cycles und Datenbankverbindungen macht
                time.sleep(2)

        RadiotracksLog.log("AdvancedHost","Thread exited")

    #Beendet den Thread. (void - Funktion)
    def stopHosting(self):
        self.keeprunning = False
        RadiotracksLog.log("AdvancedHost","Stopped hosting (please wait for pending hosting-Threads to finish)")