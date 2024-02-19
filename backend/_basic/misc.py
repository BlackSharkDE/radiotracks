########################################################################################################################################################################
#
# Sonstige, allgemeine Dinge, die in mehreren Komponenten benötigt werden
#
#########################################################################################################################################################################

import random
from concurrent.futures import ThreadPoolExecutor

from .settings import getSetting

#########################################################################################################################################################################
#-- Generelles --

#Gibt eine Zufallszahl zurück
#@param Int  Minimaler Wert (OPTIONAL)
#@param Int  Maximaler Wert (OPTIONAL)
#@return Int Zufallszahl
def getRandomness(minVal = 1, maxVal = 100):
    return random.randint(minVal,maxVal)

#Gibt zufälligen, validen Index einer Liste zurück
#@param List Eine Liste
#@param Int  Länge der Liste (OPTIONAL)
#@return Int Ein Index zwischen 0 und dem maximalen Index (inklusive) / -1 wenn die Liste leer ist
def getRandomListIndex(aList, listLen = 0):
    #Prüfe, ob Listenlänge angegeben wurde
    if listLen <= 0:
        listLen = len(aList)
    
    #Wenn Länge der Liste valide
    if listLen > 0:
        return getRandomness(0,listLen - 1)
    
    return -1

#Gibt ein zufälliges Item aus einer Liste zurück
#@param List  Eine Liste mit beliebigen Elementen
#@param bool  Ob das Item aus der Liste gelöscht werden soll (OPTIONAL)
#@return Item Ein Item aus der Liste / None, wenn die Liste leer ist
def getRandomItemFromList(givenList,deleteItemFromList = False):
    le = len(givenList)
    randomIndex = getRandomListIndex(givenList,le)
    if randomIndex > -1:
        item = givenList[randomIndex]
        if deleteItemFromList:
            givenList.pop(randomIndex)
        return item
    return None

#Prüft, ob ein Index in einer Liste existiert
#@param List  Liste mit Daten, die auf den Index geprüft werden soll
#@param Int   Index, der geprüft werden soll
#@return bool True wenn ja / False wenn nein
def indexExistsInList(listToTest,indexToTest):
    if (indexToTest >= 0) and (indexToTest < len(listToTest)):
        return True
    return False

#########################################################################################################################################################################
#-- Nebenläufigkeit --

#Konstante für maximale Anzahl an Workern eines ThreadPoolExecutor
THREAD_POOL_EXECUTOR_MAX_THREADS = getSetting("general")["threadPoolExecutorMaxWorkers"]

#Erstellt ein neues "ThreadPoolExecutor"-Objekt
#@return ThreadPoolExecutor Der neue ThreadPoolExecutor
def getNewThreadPoolExecutor():
    return ThreadPoolExecutor(THREAD_POOL_EXECUTOR_MAX_THREADS)

#Führt Funktionen mittels eines ThreadPoolExecutor aus. (void - Funktion)
#Pointer Pointer zur Funktion, die in mehreren Threads gleichzeitig ausgeführt werden soll => Die Funktion darf nur einen Parameter annehmen
#List    Liste mit Werten => Jeder der Werte wird in einen neuen Thread mit der übergebenen Funktion ausgeführt
def runMultithreadedTask(workerFunction,listOfSingularArgument):

    #Neuen ThreadPoolExecutor erstellen
    tp = getNewThreadPoolExecutor()

    #Jeden der Werte in eine Thread-Instanz packen
    for argument in listOfSingularArgument:
        #Funktionspointer, Wert für Funktion
        tp.submit(workerFunction,argument)

    #Den ThreadPoolExecutor beenden (wartet auf Beenden der Tasks)
    tp.shutdown(wait=True,cancel_futures=False)