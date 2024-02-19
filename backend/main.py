################################################################################################################################################
#
# Backend-Konsole des Servers
#
################################################################################################################################################

import os
from argparse import ArgumentParser

from _basic import RadiotracksDBConnection, RadiotracksLog, getSetting
from api import RadiotracksAPI

################################################################################################################################################
#-- Logo / Menü --

#Konstante für das Logo
LOGO = """
__________             .___.__        __                        __            
\______   \_____     __| _/|__| _____/  |_____________    ____ |  | __  ______
 |       _/\__  \   / __ | |  |/  _ \   __\_  __ \__  \ _/ ___\|  |/ / /  ___/
 |    |   \ / __ \_/ /_/ | |  (  <_> )  |  |  | \// __ \\\  \___|    <  \___ \ 
 |____|_  /(____  /\____ | |__|\____/|__|  |__|  (____  /\___  >__|_ \/____  >
        \/      \/      \/                            \/     \/     \/     \/ 
                               - backend v4 -
"""

#Konstante, ob das Logo in rot ausgegeben werden soll
USE_COLORED_LOGO = getSetting("general")["useColoredLogo"]

#Gibt das Menü von Radiotracks aus. (void - Funktion)
def showOptions():

    global LOGO
    global USE_COLORED_LOGO

    if USE_COLORED_LOGO:
        from colorama import init, Fore, Style
        init() #Init von colorama
        print(Fore.RED + LOGO) #Logo in roter Schrift ausgeben
        print(Style.RESET_ALL) #Style wieder zurücksetzen (WICHTIG)
    else:
        print(LOGO) #Normale Textausgabe

    #Optionen
    print("\nX - EXIT")
    print("C - Clear console")
    print("0 - Start/Stop all components")
    print("1 - Run Indexer manually")
    print("2 - Start/Stop IndexerManager")
    print("3 - Start/Stop AdvancedHost")
    print("4 - Start/Stop Curator")
    print("5 - Start/Stop API")
    print("")

################################################################################################################################################
#-- IndexerManager-Thread --

from indexer import IndexerManager

indexerManager = None

#Startet/Stoppt den IndexerManager. (void-Funktion)
def startStopIndexerManager():
    global indexerManager
    if indexerManager is None:
        startIndexerManager()
    else:
        stopIndexerManager()

#Startet den den IndexerManager. (void-Funktion)
def startIndexerManager():
    global indexerManager
    if indexerManager is None:
        indexerManager = IndexerManager()
        indexerManager.start()

#Stoppt den IndexerManager. (void-Funktion)
def stopIndexerManager():
    global indexerManager
    if indexerManager is not None:
        indexerManager.stopIndexing()
        indexerManager = None

################################################################################################################################################
#-- AdvancedHost-Thread --

from hosting import AdvancedHost

advancedHost = None

#Startet/Stoppt den AdvancedHost. (void-Funktion)
def startStopAdvancedHost():
    global advancedHost
    if advancedHost is None:
        startAdvancedHost()
    else:
        stopAdvancedHost()

#Startet den AdvancedHost. (void-Funktion)
def startAdvancedHost():
    global advancedHost
    if advancedHost is None:
        advancedHost = AdvancedHost()
        advancedHost.start()

#Stoppt den AdvancedHost. (void-Funktion)
def stopAdvancedHost():
    global advancedHost
    if advancedHost is not None:
        advancedHost.stopHosting()
        advancedHost = None

################################################################################################################################################
#-- Curator-Thread --

from curating import Curator

curator = None

#Startet/Stoppt den Curator. (void-Funktion)
def startStopCurator():
    global curator
    if curator is None:
        startCurator()
    else:
        stopCurator()

#Startet den Curator. (void-Funktion)
def startCurator():
    global curator
    if curator is None:
        curator = Curator()
        curator.start()

#Stoppt den Curator. (void-Funktion)
def stopCurator():
    global curator
    if curator is not None:
        curator.stopCurating()
        curator = None

################################################################################################################################################
#-- Funktionen zum Backend selbst --

#Stoppt das Radiotracks Backend. (void - Funktion)
def stopRadiotracks():
    global keeprunning
    global indexerManager
    global advancedHost
    global curator

    RadiotracksLog.log("Main","Shutting down...")

    #IndexerManager-Thread beenden
    stopIndexerManager()

    #AdvancedHost-Thread beenden
    stopAdvancedHost()

    #Curator-Thread beenden
    stopCurator()

    #API beenden
    RadiotracksAPI.stopApi()

    #Endlosschleife des Backends beenden
    keeprunning = False

#Zum leeren der Konsole
clearConsole = lambda: os.system('cls' if os.name=="nt" else 'clear')

################################################################################################################################################
# -- Menü / Main --

#Solange wird der Main-Thread (diese Datei) ausgeführt
keeprunning = True

if __name__ == '__main__':

    #Datenbankverbindung herstellen (nur zum Test für initiales Setup)
    RadiotracksDBConnection.loadSettings() #Settings für Datenbankverbindungen laden
    databaseConnection = RadiotracksDBConnection(True)
    databaseConnection.closeDatabaseConnection()

    #Definiere den Parser für die Startparameter und die Parameter selbst
    argumentParser = ArgumentParser(prog="main.py",description="The API of Radiotracks v4.",epilog="----")
    argumentParser.add_argument(
        "-a","--autostart",  #Parameternamen
        action='store_true', #Damit der Parameter standardmäßig False ist und nur True wird wenn dieser angegeben wurde
        help="automatically starts all components of the server" #Informationen für die Hilfe
    )

    #Gibt ein "Namespace"-Objekt zurück, dies mittels vars() in ein Dictionary konvertieren (Keys werden zuletzt angegebene Parameter-Namen)
    arguments = vars(argumentParser.parse_args())

    showOptions()

    #Wenn Autostart-Paramter angegeben wurde
    if arguments["autostart"]:
        RadiotracksLog.log("Main","Argument for autostart detected, starting all components...")
        startIndexerManager()
        startAdvancedHost()
        startCurator()
        RadiotracksAPI.startApi()

    while keeprunning:

        serverCommand = str(input(''))        #Command-Eingabe
        serverCommand = serverCommand.strip() #Leerzeichen entfernen (am Anfang und Ende)
        serverCommand = serverCommand.lower() #Kleinschreiben (besserer Vergleich möglich)

        if serverCommand == "x":
            stopRadiotracks()
        elif serverCommand == "c":
            clearConsole()
            showOptions()
        elif serverCommand == "0":
            startStopIndexerManager()
            startStopAdvancedHost()
            startStopCurator()
            RadiotracksAPI.startStopApi()
        elif serverCommand == "1":
            if indexerManager is None:
                startIndexerManager()
            indexerManager.runManually()
        elif serverCommand == "2":
            startStopIndexerManager()
        elif serverCommand == "3":
            startStopAdvancedHost()
        elif serverCommand == "4":
            startStopCurator()
        elif serverCommand == "5":
            RadiotracksAPI.startStopApi()