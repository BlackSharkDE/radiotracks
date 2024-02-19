########################################################################################################################################################################
#
# IndexerManager
#
# Management der Indexer
#
########################################################################################################################################################################

import threading
import datetime
import time

from _basic import getSetting, RadiotracksLog, getNewThreadPoolExecutor
from .indexer import Indexer

########################################################################################################################################################################

class IndexerManager(threading.Thread):
    
    #-- Konstruktor --
    def __init__(self):
        threading.Thread.__init__(self) #Parent-Konstruktor (Thread)

        #Für Endlosschleife in "run"-Methode
        self.keeprunning = True

        #Sorgt dafür, dass Thread einmal manuell durchläuft (umgeht Zeitrestriktion für einen Cycle)
        self.manualRun = False

        #Einstellungen für den Thread laden
        indexerSettings       = getSetting("indexing")
        self.executionHour    = indexerSettings["executionHour"]
        self.executionMinutes = indexerSettings["executionMinutes"]

        #Ein Indexer-Objekt
        self.indexer = Indexer()

        #Threads für Indexer
        self.indexerMethods = [self.indexer.indexArtists,self.indexer.indexAuthors,self.indexer.indexChannels,self.indexer.indexCuratedPlaylists,self.indexer.indexPodcasts]
    
    #Thread-Methode (void - Funktion)
    def run(self):
        RadiotracksLog.log("IndexerManager","Thread started - Schedule for daily at " + str(self.executionHour).zfill(2) + ":" + str(self.executionMinutes).zfill(2) + " o'clock")

        #Verhindert, dass der Indexer mehrmals hintereinander ausgeführt wird
        ranToday = False

        #So lange bis nicht mehr ausgeführt werden soll
        while self.keeprunning:

            #Uhrzeit jetzt
            now = datetime.datetime.now()

            #Wenn die Uhrzeit der Ausführungszeit entspricht und heute noch nicht ausgeführt wurde ODER Manuell ausgeführt wird
            if ((now.minute == self.executionMinutes and now.hour == self.executionHour) and ranToday == False) or (self.manualRun == True):

                #Threads für die verschiedenen Indexer erstellen -> Siehe "runMultithreadedTask" in "_basic" für Funktionsweise
                tp = getNewThreadPoolExecutor()
                for method in self.indexerMethods:
                    tp.submit(method)
                tp.shutdown(wait=True,cancel_futures=False)

                #Prüfe, ob Durchlauf manuell war
                if self.manualRun == True:
                    #Manuell
                    RadiotracksLog.log("IndexerManager","Done with manual run")
                    self.manualRun = False
                else:
                    #Automatisch
                    ranToday = True
                    RadiotracksLog.log("IndexerManager","Done with indexing for today")

            elif (now.minute > self.executionMinutes and now.hour > self.executionHour) and ranToday == True:
                #Zurücksetzen der Sperrvariable für automatische Durchläufe
                ranToday = False
                RadiotracksLog.log("IndexerManager","Reset for next indexing run tomorrow")

            #Verhindere, dass der Thread zu viele Cycles macht
            time.sleep(1)

    #Beendet den Thread. (void - Funktion)
    def stopIndexing(self):
        self.keeprunning = False
        RadiotracksLog.log("IndexerManager","Thread stopped")

    #Stößt den Indexer-Durchlauf manuell an. (void - Funktion)
    def runManually(self):
        RadiotracksLog.log("IndexerManager","Starting manual run...")
        self.manualRun = True